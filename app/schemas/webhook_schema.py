from typing import List, Optional

from pydantic import BaseModel



#
# Azure DevOps Repository Schema
#

class RepositorySchema(BaseModel):

    id: Optional[str] = None

    name: Optional[str] = None

    url: Optional[str] = None



#
# Azure DevOps Commit Schema
#

class CommitSchema(BaseModel):

    commitId: str

    author: Optional[dict] = None

    committer: Optional[dict] = None

    comment: Optional[str] = None

    url: Optional[str] = None



#
# Branch Reference Schema
#

class RefUpdateSchema(BaseModel):

    name: Optional[str] = None

    oldObjectId: Optional[str] = None

    newObjectId: Optional[str] = None



#
# Push Resource Schema
#

class PushResourceSchema(BaseModel):

    commits: List[CommitSchema] = []

    repository: RepositorySchema

    refUpdates: List[RefUpdateSchema] = []



#
# Azure DevOps Service Hook Payload
#

class AzureDevOpsPushEventSchema(BaseModel):

    createdDate: Optional[str] = None

    eventType: Optional[str] = None

    resourceVersion: Optional[str] = None

    resource: PushResourceSchema



#
# Webhook Response
#

class WebhookResponseSchema(BaseModel):

    status: str

    message: Optional[str] = None

    commit_id: Optional[str] = None

    branch: Optional[str] = None