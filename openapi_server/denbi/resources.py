""" Module contains classes  GPUResources and GPUResourcesException."""
import openapi_server.denbi

from openapi_server.models.flavor_gpu import FlavorGPU


class GPUResources: # pylint: disable=too-many-instance-attributes
    """
    Generates a data structure containing all gpu hypervisors with available resources.
    Additional the count of all possible flavor can be calculated.
    """

    def __init__(self, cpu_overprovisioning=4):
        self.__osclient__ = openapi_server.denbi.create_osclient()

        self.__hypervisors__ = {}
        self.__gpu_aggregates__ = []
        self.__gpu_instances_by_host__ = {}

        self.__map_of_aggregates__ = {}
        self.__map_of_hypervisors__ = {}
        self.__gpu_flavors__ = []

        self.cpu_overprovisioning = cpu_overprovisioning

    def __update_aggregates__(self):
        """
        Collect information about if used and availed resources considering GPU based hypervisor only and update
        internal data structure.
        """

        result = {}

        for hypervisor in self.__osclient__.list_hypervisors():
            self.__hypervisors__[hypervisor["name"].split('.')[0]] = hypervisor

        for aggregate in self.__gpu_aggregates__:

            # collect all gpu hypervisor of this aggregate
            gpu_hypervisors = []
            for hostname in aggregate["hosts"]:
                # determine number of used gpus
                used = 0
                if hostname in self.__gpu_instances_by_host__.keys():
                    for instance in self.__gpu_instances_by_host__[hostname]:
                        used = used + int(instance["flavor"]["extra_specs"]["pci_passthrough:alias"].split(":")[1])

                hypervisor = self.__hypervisors__[hostname]

                gpu_hypervisors.append({"name": hypervisor["name"].split('.')[0],
                                        "status": hypervisor["status"],
                                        "state": hypervisor["state"],
                                        "running_vms": int(hypervisor['running_vms']),
                                        "gpus": int(aggregate["metadata"]['gpu_count']),
                                        "gpu_type": aggregate["metadata"]["gpu_type"],
                                        "gpus_used": int(used),
                                        "vcpus": int(hypervisor["vcpus"]),
                                        "vcpus_used": int(hypervisor["vcpus_used"]),
                                        "memory": int(int(hypervisor["memory_size"]) / 1024),  # in GB
                                        "memory_free": int(int(hypervisor["memory_free"]) / 1024),  # in GB
                                        "disk": int(hypervisor["local_disk_size"]),  # in GB
                                        "disk_available": int(hypervisor["disk_available"]),  # in GB
                                        })

            # add necessary aggregate information to datastructure
            result[aggregate["name"]] = {}
            result[aggregate["name"]]["gpu_type"] = aggregate["metadata"]["gpu_type"]
            result[aggregate["name"]]["gpu_count"] = int(aggregate["metadata"]['gpu_count'])
            result[aggregate["name"]]["hypervisors"] = gpu_hypervisors

        self.__map_of_aggregates__ = result

    def __update_gpu_flavors__(self):
        """
        Internal helper functions, that calculates available and total number of GPU flavors.
        """

        gpu_flavors = []

        for flavor in self.__osclient__.list_flavors(): # pylint: disable=too-many-nested-blocks
            if "pci_passthrough:alias" in flavor["extra_specs"].keys() and \
                    flavor["is_disabled"] != "false" and \
                    flavor["name"].find("DEPRECATED") == -1:
                total = 0
                available = 0
                # get cpu type and count
                gpu_type, gpu_count = flavor["extra_specs"]["pci_passthrough:alias"].split(":")
                # sum up all local disk space disk and ephemeral are measured in GB, swap in MB
                local_disk = flavor["disk"] + flavor["ephemeral"]
                if flavor["swap"] > 0:
                    local_disk += int(flavor["swap"] / 1024)
                # iterate over all gpu aggregates
                for aggegrate in self.__map_of_aggregates__.values():
                    # if aggregate matches flavor gpu type
                    if aggegrate["gpu_type"] == gpu_type:
                        # iterate over all hypervisor of current aggregate
                        for hypervisor in aggegrate["hypervisors"]:
                            # total number of flavors possible on an empty hypervisor
                            # calculate availability of each resource type
                            t_gpu = int(hypervisor["gpus"] / int(gpu_count))
                            t_vcpu = int(
                                int(hypervisor["vcpus"]) * self.cpu_overprovisioning / int(flavor["vcpus"]))
                            t_mem = int(int(hypervisor["memory"]) / int(flavor["ram"] / 1024))
                            t_disk = int(int(hypervisor["disk"] / local_disk))
                            # add minimum of all resources needed to total number
                            total += min(t_gpu, t_vcpu, t_mem, t_disk)
                            # number of flavors possible with current available resources
                            c_gpu = int((hypervisor["gpus"] - hypervisor["gpus_used"]) / int(gpu_count))
                            c_vcpu = int((int(hypervisor["vcpus"]) * self.cpu_overprovisioning - int(
                                hypervisor["vcpus_used"])) / int(flavor["vcpus"]))
                            c_mem = int(int(hypervisor["memory_free"]) / int(flavor["ram"] / 1024))
                            c_disk = int(int(hypervisor["disk_available"] / local_disk))
                            if min(c_gpu, c_vcpu, c_mem, c_disk) < 0:
                                print(f"{c_gpu} {c_vcpu} {c_mem} {c_disk} {min(c_gpu, c_vcpu, c_mem, c_disk)}")
                            available += min(c_gpu, c_vcpu, c_mem, c_disk)

                gpu_flavors.append(FlavorGPU(flavor_name=flavor["name"],
                                             flavor_openstack_id=flavor["id"],
                                             available=available,
                                             total=total))
            self.__gpu_flavors__ = gpu_flavors

    def __update_gpu_aggregates__(self):
        """
        Helper method. Update list of GPU aggregates.
        """
        for aggregate in self.__osclient__.list_aggregates():
            if "gpu" in aggregate["metadata"].keys():
                self.__gpu_aggregates__.append(aggregate)

    def __update_gpu_instances_by_host__(self):
        """
        Helper method. Update map of gpu instances by host.
        """
        for instance in self.__osclient__.list_servers(all_projects=True):
            # Filter all GPU instances
            if "pci_passthrough:alias" in instance["flavor"]["extra_specs"].keys():
                if instance["host"] not in self.__gpu_instances_by_host__.keys():
                    self.__gpu_instances_by_host__[instance["host"]] = []
                self.__gpu_instances_by_host__[instance["host"]].append(instance)

    def update(self):
        """
        Update internal datastructures, calculates the number of total and available
        GPU flavors.
        """
        self.__update_gpu_aggregates__()
        self.__update_gpu_instances_by_host__()
        self.__update_aggregates__()
        self.__update_gpu_flavors__()

    def gpu_flavors(self):
        """
        Return a possible empty list of FlavorGPU objects.

        :return: List of FlavorGPU objects
        """
        return self.__gpu_flavors__

    def gpu_flavor(self, flavorid):
        """
        Return FlavorGPU with given id. Raise exception in case of non existing id.

        :param flavorid: id of flavor
        :return: FlavorGPU object with given id
        """
        for flavor in self.__gpu_flavors__:
            if flavor.flavor_openstack_id == flavorid:
                return flavor
        raise GPUResourceException("Unknown flavor id!")


class GPUResourceException(Exception):
    """ GPUResourceException to avoid throwing a general exception."""

    def __init__(self, msg):
        super().__init__(f"GPUResource: {msg}")
