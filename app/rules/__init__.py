"""
Deterministic Risk Rules Package.

This package contains all static
DevOps risk detection rules.

Available rule groups:

- Security Rules
- Terraform Rules
- Kubernetes Rules
- Pipeline Rules
- Coding Rules
"""



from app.rules.security_rules import (
    security_rules
)

from app.rules.terraform_rules import (
    terraform_rules
)

from app.rules.kubernetes_rules import (
    kubernetes_rules
)

from app.rules.pipeline_rules import (
    pipeline_rules
)

from app.rules.coding_rules import (
    coding_rules
)
from app.rules.platform_rules import platform_rules



#
# Register all rules
#

ALL_RULES = [

    *security_rules,

    *terraform_rules,

    *kubernetes_rules,

    *pipeline_rules,

    *coding_rules,
    *platform_rules

]



def get_all_rules():

    """
    Returns all registered
    deterministic rules.
    """

    return ALL_RULES
