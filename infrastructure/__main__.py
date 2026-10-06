import pulumi
from pulumi_kubernetes.apps.v1 import Deployment, DeploymentSpecArgs
from pulumi_kubernetes.core.v1 import (
    ContainerArgs,
    ContainerPortArgs,
    EnvVarArgs,
    PodSpecArgs,
    PodTemplateSpecArgs,
    Service,
    ServicePortArgs,
    ServiceSpecArgs,
)
from pulumi_kubernetes.meta.v1 import LabelSelectorArgs, ObjectMetaArgs
from pulumi_kubernetes.networking.v1 import (
    HTTPIngressPathArgs,
    HTTPIngressRuleValueArgs,
    Ingress,
    IngressBackendArgs,
    IngressRuleArgs,
    IngressServiceBackendArgs,
    IngressSpecArgs,
    ServiceBackendPortArgs,
)

# ------------------------------------------------------------------------------
# 1. POSTGRESQL DATABASE
# ------------------------------------------------------------------------------
postgres_labels = {"app": "postgres"}

postgres_deployment = Deployment(
    "postgres-deployment",
    spec=DeploymentSpecArgs(
        selector=LabelSelectorArgs(match_labels=postgres_labels),
        template=PodTemplateSpecArgs(
            metadata=ObjectMetaArgs(labels=postgres_labels),
            spec=PodSpecArgs(
                containers=[
                    ContainerArgs(
                        name="postgres",
                        image="postgres:15-alpine",
                        ports=[ContainerPortArgs(container_port=5432)],
                        env=[
                            EnvVarArgs(name="POSTGRES_DB", value="appdb"),
                            EnvVarArgs(name="POSTGRES_USER", value="postgres"),
                            EnvVarArgs(name="POSTGRES_PASSWORD", value="postgres"),
                        ],
                    )
                ]
            ),
        ),
    ),
)

postgres_service = Service(
    "postgres-service",
    spec=ServiceSpecArgs(
        selector=postgres_labels,
        ports=[ServicePortArgs(port=5432, target_port=5432)],
    ),
)

# ------------------------------------------------------------------------------
# 2. AUTH SERVICE
# ------------------------------------------------------------------------------
auth_labels = {"app": "auth-service"}

auth_deployment = Deployment(
    "auth-service-deployment",
    spec=DeploymentSpecArgs(
        replicas=2,
        selector=LabelSelectorArgs(match_labels=auth_labels),
        template=PodTemplateSpecArgs(
            metadata=ObjectMetaArgs(labels=auth_labels),
            spec=PodSpecArgs(
                containers=[
                    ContainerArgs(
                        name="auth-service",
                        image="feim755/auth-service:latest",
                        image_pull_policy="Never",
                        ports=[ContainerPortArgs(container_port=5000)],
                        env=[
                            EnvVarArgs(
                                name="DATABASE_URL",
                                value="postgresql://postgres:postgres@postgres-service:5432/appdb",
                            )
                        ],
                    )
                ]
            ),
        ),
    ),
)

auth_service = Service(
    "auth-service",
    spec=ServiceSpecArgs(
        selector=auth_labels,
        ports=[ServicePortArgs(port=5000, target_port=5000)],
    ),
)

# ------------------------------------------------------------------------------
# 3. DATA SERVICE
# ------------------------------------------------------------------------------
data_labels = {"app": "data-service"}

data_deployment = Deployment(
    "data-service-deployment",
    spec=DeploymentSpecArgs(
        replicas=2,
        selector=LabelSelectorArgs(match_labels=data_labels),
        template=PodTemplateSpecArgs(
            metadata=ObjectMetaArgs(labels=data_labels),
            spec=PodSpecArgs(
                containers=[
                    ContainerArgs(
                        name="data-service",
                        image="feim755/data-service:latest",
                        image_pull_policy="Never",
                        ports=[ContainerPortArgs(container_port=5001)],
                        env=[
                            EnvVarArgs(
                                name="DATABASE_URL",
                                value="postgresql://postgres:postgres@postgres-service:5432/appdb",
                            )
                        ],
                    )
                ]
            ),
        ),
    ),
)

data_service = Service(
    "data-service",
    spec=ServiceSpecArgs(
        selector=data_labels,
        ports=[ServicePortArgs(port=5001, target_port=5001)],
    ),
)

# ------------------------------------------------------------------------------
# 4. INGRESS CONTROLLER ROUTING
# ------------------------------------------------------------------------------
ingress = Ingress(
    "platform-ingress",
    metadata=ObjectMetaArgs(
        annotations={
            "kubernetes.io/ingress.class": "nginx",
            "nginx.ingress.kubernetes.io/rewrite-target": "/$2",
            "nginx.ingress.kubernetes.io/use-regex": "true",
        }
    ),
    spec=IngressSpecArgs(
        rules=[
            IngressRuleArgs(
                http=HTTPIngressRuleValueArgs(
                    paths=[
                        HTTPIngressPathArgs(
                            path="/auth(/|$)(.*)",
                            path_type="ImplementationSpecific",
                            backend=IngressBackendArgs(
                                service=IngressServiceBackendArgs(
                                    name=auth_service.metadata["name"],
                                    port=ServiceBackendPortArgs(number=5000),
                                )
                            ),
                        ),
                        HTTPIngressPathArgs(
                            path="/data(/|$)(.*)",
                            path_type="ImplementationSpecific",
                            backend=IngressBackendArgs(
                                service=IngressServiceBackendArgs(
                                    name=data_service.metadata["name"],
                                    port=ServiceBackendPortArgs(number=5001),
                                )
                            ),
                        ),
                    ]
                )
            )
        ]
    ),
)

# Exports
pulumi.export("postgres_service_name", postgres_service.metadata["name"])
pulumi.export("auth_service_name", auth_service.metadata["name"])
pulumi.export("data_service_name", data_service.metadata["name"])