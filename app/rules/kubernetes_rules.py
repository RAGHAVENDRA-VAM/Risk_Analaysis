from typing import (
    List,
    Dict
)


from app.core.logging import (
    get_logger
)





logger = get_logger(
    __name__
)





class KubernetesRules:
    """
    Kubernetes security rules.
    """



    def __init__(self):

        self.name = "kubernetes"





    def evaluate(
        self,
        context: Dict
    ) -> List[Dict]:

        """
        Execute Kubernetes checks.
        """

        findings = []



        for file in context.get(
            "files",
            []
        ):


            if file.get(
                "category"
            ) != "kubernetes":

                continue



            path = file.get(
                "path",
                ""
            )


            content = file.get(
                "content",
                ""
            )



            findings.extend(
                self.check_privileged_container(
                    path,
                    content
                )
            )


            findings.extend(
                self.check_running_as_root(
                    path,
                    content
                )
            )


            findings.extend(
                self.check_resource_limits(
                    path,
                    content
                )
            )


            findings.extend(
                self.check_public_service(
                    path,
                    content
                )
            )


            findings.extend(
                self.check_latest_image(
                    path,
                    content
                )
            )



        return findings





    def check_privileged_container(
        self,
        path: str,
        content: str
    ):

        """
        Detect privileged containers.
        """

        findings = []



        if (
            "privileged: true"
            in content.lower()
        ):


            findings.append(

                {

                    "rule":
                        "K8S_PRIVILEGED_CONTAINER",


                    "title":
                        "Privileged Container Enabled",


                    "severity":
                        "CRITICAL",


                    "score":
                        100,


                    "file":
                        path,


                    "description":
                        "Container has privileged access"

                }

            )


        return findings





    def check_running_as_root(
        self,
        path: str,
        content: str
    ):

        """
        Detect containers running as root.
        """

        findings = []



        if (

            "securityContext"
            not in content

            or

            "runAsNonRoot: true"
            not in content

        ):


            findings.append(

                {

                    "rule":
                        "K8S_RUNNING_AS_ROOT",


                    "title":
                        "Container Running As Root",


                    "severity":
                        "HIGH",


                    "score":
                        80,


                    "file":
                        path,


                    "description":
                        "Container does not enforce non-root execution"

                }

            )


        return findings





    def check_resource_limits(
        self,
        path: str,
        content: str
    ):

        """
        Detect missing CPU/memory limits.
        """

        findings = []



        if (

            "resources:"
            not in content

        ):


            findings.append(

                {

                    "rule":
                        "K8S_MISSING_RESOURCE_LIMITS",


                    "title":
                        "Missing Container Resource Limits",


                    "severity":
                        "MEDIUM",


                    "score":
                        50,


                    "file":
                        path,


                    "description":
                        "CPU and memory limits are not configured"

                }

            )


        return findings





    def check_public_service(
        self,
        path: str,
        content: str
    ):

        """
        Detect public Kubernetes services.
        """

        findings = []



        if (

            "type: LoadBalancer"
            in content

        ):


            findings.append(

                {

                    "rule":
                        "K8S_PUBLIC_SERVICE",


                    "title":
                        "Public Service Exposure",


                    "severity":
                        "HIGH",


                    "score":
                        75,


                    "file":
                        path,


                    "description":
                        "Service exposed through public load balancer"

                }

            )


        return findings





    def check_latest_image(
        self,
        path: str,
        content: str
    ):

        """
        Detect mutable image tags.
        """

        findings = []



        if (

            ":latest"
            in content

        ):


            findings.append(

                {

                    "rule":
                        "K8S_LATEST_IMAGE",


                    "title":
                        "Latest Image Tag Used",


                    "severity":
                        "MEDIUM",


                    "score":
                        40,


                    "file":
                        path,


                    "description":
                        "Container uses non-versioned image tag"

                }

            )


        return findings