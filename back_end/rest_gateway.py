from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low
from typing import Optional, Any, Dict

# Create REST Gateway Agent
gateway_agent = Agent(
    name="rest_gateway",
    port=8006,
    seed="rest_gateway_seed_12345",
    endpoint=["http://127.0.0.1:8006/submit"]
)

EXTRACTOR_ADDRESS = "agent1qwcrrpsgl49tqn50gmsyesq48g3v7mchzmhr6074tn94fw8dqzepxxds4vm"
CURATOR_ADDRESS = "agent1qdr8zekrarc5hhyhxju7suyr8nfxe6j8q9kgxa9007v8wmdvraw9z0uw37v"

# REST Request/Response Models
class DailyEntryRequest(Model):
    entry_text: str
    mood_rating: int
    energy_rating: int
    user_id: str = "default_user"

class FeedbackRequest(Model):
    pattern_id: str
    feedback_type: str
    user_comment: str = ""
    user_id: str = "default_user"

class TestRequest(Model):
    test_message: str = "test"
    timestamp: Optional[str] = None

class SuccessResponse(Model):
    success: bool
    message: str
    forwarded_to: Optional[str] = None

class ErrorResponse(Model):
    success: bool
    error: str

class StatusResponse(Model):
    status: str
    gateway_address: str
    connected_agents: Dict[str, str]
    endpoints: list

# uAgent Message Models (matching other agents)
class DailyEntryMessage(Model):
    entry_text: str
    mood_rating: int
    energy_rating: int
    user_id: str = "default_user"

class UserFeedbackMessage(Model):
    pattern_id: str
    feedback_type: str
    user_comment: str
    user_id: str

@gateway_agent.on_rest_post("/daily_entry", DailyEntryRequest, SuccessResponse)
async def handle_daily_entry(ctx: Context, req: DailyEntryRequest) -> SuccessResponse:
    """Handle daily entry from Flask and forward to extractor agent"""
    try:
        ctx.logger.info(f"REST Gateway received daily entry from user: {req.user_id}")
        
        # Create message for extractor agent (using proper Model)
        entry_msg = DailyEntryMessage(
            entry_text=req.entry_text,
            mood_rating=req.mood_rating,
            energy_rating=req.energy_rating,
            user_id=req.user_id
        )
        
        # Send to extractor agent
        await ctx.send(EXTRACTOR_ADDRESS, entry_msg)
        ctx.logger.info(f"Forwarded daily entry to extractor agent")
        
        return SuccessResponse(
            success=True,
            message="Daily entry forwarded to extractor agent",
            forwarded_to=EXTRACTOR_ADDRESS
        )
        
    except Exception as e:
        ctx.logger.error(f"Error handling daily entry: {e}")
        return SuccessResponse(
            success=False,
            message=f"Error: {str(e)}"
        )

@gateway_agent.on_rest_post("/feedback", FeedbackRequest, SuccessResponse)
async def handle_feedback(ctx: Context, req: FeedbackRequest) -> SuccessResponse:
    """Handle feedback from Flask and forward to curator agent"""
    try:
        ctx.logger.info(f"REST Gateway received feedback for pattern: {req.pattern_id}")
        
        # Create message for curator agent (using proper Model)
        feedback_msg = UserFeedbackMessage(
            pattern_id=req.pattern_id,
            feedback_type=req.feedback_type,
            user_comment=req.user_comment,
            user_id=req.user_id
        )
        
        # Send to curator agent
        await ctx.send(CURATOR_ADDRESS, feedback_msg)
        ctx.logger.info(f"Forwarded feedback to curator agent")
        
        return SuccessResponse(
            success=True,
            message="Feedback forwarded to curator agent",
            forwarded_to=CURATOR_ADDRESS
        )
        
    except Exception as e:
        ctx.logger.error(f"Error handling feedback: {e}")
        return SuccessResponse(
            success=False,
            message=f"Error: {str(e)}"
        )

@gateway_agent.on_rest_get("/status", StatusResponse)
async def get_status(ctx: Context) -> StatusResponse:
    """Get gateway status"""
    try:
        return StatusResponse(
            status="online",
            gateway_address=str(gateway_agent.address),
            connected_agents={
                "extractor": EXTRACTOR_ADDRESS,
                "curator": CURATOR_ADDRESS
            },
            endpoints=["/daily_entry", "/feedback", "/status", "/test"]
        )
    except Exception as e:
        ctx.logger.error(f"Error getting status: {e}")
        return StatusResponse(
            status="error",
            gateway_address=str(gateway_agent.address),
            connected_agents={},
            endpoints=[]
        )

@gateway_agent.on_rest_post("/test", TestRequest, SuccessResponse) 
async def test_endpoint(ctx: Context, req: TestRequest) -> SuccessResponse:
    """Test endpoint for connectivity"""
    try:
        ctx.logger.info(f"Test request received: {req}")
        return SuccessResponse(
            success=True,
            message="REST Gateway is working!",
            forwarded_to=f"gateway_address: {str(gateway_agent.address)}"
        )
    except Exception as e:
        ctx.logger.error(f"Error in test endpoint: {e}")
        return SuccessResponse(
            success=False,
            message=f"Test failed: {str(e)}"
        )

@gateway_agent.on_event("startup")
async def startup_handler(ctx: Context):
    ctx.logger.info("REST Gateway Agent Starting...")
    ctx.logger.info(f"Address: {gateway_agent.address}")
    ctx.logger.info(f"Endpoints: http://127.0.0.1:8006")
    ctx.logger.info("Ready to bridge Flask and uAgent Network")

if __name__ == "__main__":
    print("Starting REST Gateway...")
    print("=" * 50)
    print("Gateway will run on: http://127.0.0.1:8006")
    print("Available endpoints:")
    print("   POST /daily_entry - Forward entries to extractor")
    print("   POST /feedback - Forward feedback to curator") 
    print("   GET /status - Gateway status")
    print("   POST /test - Test connectivity")
    print("=" * 50)
    
    gateway_agent.run()