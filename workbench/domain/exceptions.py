"""
Domain exceptions for AI Video Workbench Phase 1.
"""

class WorkbenchError(Exception):
    """Base exception for all workbench domain errors."""
    pass

class InsufficientBalanceError(WorkbenchError):
    """Raised when account balance is lower than the safety threshold (Cost * 120%)."""
    def __init__(self, current_balance: float, estimated_cost: float, required_balance: float):
        self.current_balance = current_balance
        self.estimated_cost = estimated_cost
        self.required_balance = required_balance
        super().__init__(
            f"Pre-flight FinOps Gate Blocked: Current balance ${current_balance:.4f} is lower than "
            f"required ${required_balance:.4f} (120% of estimated cost ${estimated_cost:.4f})."
        )

class InpaintingExceededError(WorkbenchError):
    """Raised when human reviewer exceeds the maximum allowed inpainting retries per shot."""
    def __init__(self, shot_id: str, retry_count: int, max_retries: int):
        self.shot_id = shot_id
        self.retry_count = retry_count
        self.max_retries = max_retries
        super().__init__(
            f"Shot {shot_id} exceeded maximum inpainting retries ({retry_count}/{max_retries}). "
            f"Potential semantic conflict between start and end frames; recommend full regeneration."
        )

class InvalidStateTransitionError(WorkbenchError):
    """Raised when an illegal state machine transition is attempted."""
    def __init__(self, current_state: str, target_state: str, reason: str = ""):
        self.current_state = current_state
        self.target_state = target_state
        super().__init__(
            f"Illegal state transition from [{current_state}] to [{target_state}]. {reason}"
        )

class OpticalConflictError(WorkbenchError):
    """Raised when start frame and end frame have severe perspective or subject mismatch."""
    pass

class ExternalAPIError(WorkbenchError):
    """Raised when an external model API returns an error."""
    def __init__(self, provider: str, status_code: int, message: str):
        self.provider = provider
        self.status_code = status_code
        self.message = message
        super().__init__(f"External API error from {provider} [HTTP {status_code}]: {message}")
