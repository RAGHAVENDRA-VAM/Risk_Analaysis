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





class CommitContextBuilder:
    """
    Converts commit changes into
    AI risk analysis context.
    """



    def __init__(self):

        self.file_categories = {


            ".tf":

                "terraform",


            ".yaml":

                "kubernetes",


            ".yml":

                "kubernetes",


            "Dockerfile":

                "container",


            ".py":

                "application",


            ".java":

                "application",


            ".cs":

                "application"

        }





    def detect_file_category(
        self,
        filename: str
    ):

        """
        Identify technology type.
        """



        for extension, category in (

            self.file_categories.items()

        ):


            if filename.endswith(extension):


                return category



            if filename.endswith(

                extension

            ):


                return category





        return "unknown"





    def detect_risk_area(
        self,
        file_path: str
    ):

        """
        Identify possible risk area.
        """



        path = file_path.lower()



        if "network" in path:


            return "network"




        if "security" in path:


            return "security"




        if "iam" in path:


            return "identity"




        if "database" in path:


            return "database"




        if "terraform" in path:


            return "infrastructure"




        if "deployment" in path:


            return "deployment"



        return "general"





    def build_file_context(
        self,
        files: List[Dict]
    ):

        """
        Enrich changed files.
        """



        context_files = []



        for file in files:


            path = file.get(

                "path",

                ""

            )



            context_files.append(

                {


                "path":

                    path,


                "change_type":

                    file.get(

                        "change_type",

                        "modified"

                    ),


                "category":

                    self.detect_file_category(

                        path

                    ),


                "risk_area":

                    self.detect_risk_area(

                        path

                    )


                }

            )



        return context_files





    def build_context(
        self,
        commit_data: dict
    ):

        """
        Build complete commit context.
        """



        files = commit_data.get(

            "files",

            []

        )



        enriched_files = (

            self.build_file_context(

                files

            )

        )



        categories = list(

            set(

                file["category"]

                for file in enriched_files

            )

        )



        risk_areas = list(

            set(

                file["risk_area"]

                for file in enriched_files

            )

        )



        context = {


            "commit_id":

                commit_data.get(

                    "commit_id"

                ),



            "author":

                commit_data.get(

                    "author"

                ),



            "message":

                commit_data.get(

                    "message"

                ),



            "files":

                enriched_files,



            "technologies":

                categories,



            "risk_areas":

                risk_areas

        }



        logger.info(

            f"Commit context created "
            f"for {context['commit_id']}"

        )



        return context