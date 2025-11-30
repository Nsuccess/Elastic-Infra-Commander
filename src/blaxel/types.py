"""TypedDict definitions for Blaxel Fleet Commander tools."""

from typing_extensions import TypedDict


class SandboxInfo(TypedDict):
    """Information about a sandbox with latency."""
    name: str
    status: str
    latency_ms: float
    image: str
    memory: int


class ListSandboxesResult(TypedDict):
    """Result from fleet_list_sandboxes."""
    sandboxes: list[SandboxInfo]
    total: int


class DeploymentResult(TypedDict):
    """Result from deploying to a single sandbox."""
    sandbox_name: str
    url: str
    deploy_time_seconds: float
    status: str


class FleetDeployResult(TypedDict):
    """Result from fleet_deploy_game."""
    deployments: list[DeploymentResult]
    total_time_seconds: float
    repo_url: str
    reasoning: list[str]  # Step-by-step reasoning log


class URLVerification(TypedDict):
    """Result from verifying a single URL."""
    url: str
    live: bool
    status_code: int | None
    latency_ms: float | None


class FleetVerifyResult(TypedDict):
    """Result from fleet_verify_live."""
    verifications: list[URLVerification]
    all_live: bool
