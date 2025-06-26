#!/usr/bin/env python3
"""
Enhanced Planning Mode with Iteration and Refinement
Advanced planning system with DeepSeek AI and MCP integration
"""

import asyncio
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import logging
from pathlib import Path

# Import our modules
from deepseek_client import DeepSeekClient, PlanningContext, EnhancedPlanningEngine
from mcp_server_config import MCPServerManager, EnhancedMCPIntegration
from ideation_system import IdeationSystem, EnhancedFeatureIdeation
from framework_planner import FrameworkPlanner, ComprehensiveFrameworkPlan

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PlanningIteration:
    """Single planning iteration with evaluation"""
    iteration_number: int
    input_context: Dict[str, Any]
    planning_result: Dict[str, Any]
    evaluation_metrics: Dict[str, float]
    refinement_suggestions: List[str]
    confidence_score: float
    timestamp: datetime
    tools_used: List[str] = None
    
    def __post_init__(self):
        if self.tools_used is None:
            self.tools_used = []

@dataclass
class PlanningSession:
    """Complete planning session with multiple iterations"""
    session_id: str
    domain: str
    initial_requirements: Dict[str, Any]
    iterations: List[PlanningIteration]
    final_plan: Dict[str, Any]
    convergence_metrics: Dict[str, float]
    session_summary: Dict[str, Any]
    created_at: datetime
    completed_at: Optional[datetime] = None

@dataclass
class RefinementStrategy:
    """Strategy for refining planning iterations"""
    focus_areas: List[str]
    improvement_targets: Dict[str, float]
    refinement_techniques: List[str]
    evaluation_criteria: Dict[str, float]

class PlanningEvaluator:
    """Evaluates and scores planning iterations"""
    
    def __init__(self):
        self.evaluation_criteria = {
            "feasibility": 0.25,
            "completeness": 0.20,
            "innovation": 0.15,
            "resource_efficiency": 0.15,
            "risk_mitigation": 0.15,
            "clarity": 0.10
        }
    
    def evaluate_plan(self, plan: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, float]:
        """Evaluate a planning iteration"""
        
        metrics = {}
        
        # Feasibility assessment
        metrics["feasibility"] = self._assess_feasibility(plan, context)
        
        # Completeness check
        metrics["completeness"] = self._assess_completeness(plan)
        
        # Innovation scoring
        metrics["innovation"] = self._assess_innovation(plan)
        
        # Resource efficiency
        metrics["resource_efficiency"] = self._assess_resource_efficiency(plan)
        
        # Risk mitigation
        metrics["risk_mitigation"] = self._assess_risk_mitigation(plan)
        
        # Clarity and structure
        metrics["clarity"] = self._assess_clarity(plan)
        
        # Overall score
        metrics["overall_score"] = sum(
            metrics[criterion] * weight 
            for criterion, weight in self.evaluation_criteria.items()
            if criterion in metrics
        )
        
        return metrics
    
    def _assess_feasibility(self, plan: Dict[str, Any], context: Dict[str, Any]) -> float:
        """Assess technical and business feasibility"""
        
        feasibility_indicators = [
            "technical_requirements" in str(plan).lower(),
            "timeline" in str(plan).lower(),
            "budget" in str(plan).lower(),
            "team" in str(plan).lower(),
            "technology" in str(plan).lower()
        ]
        
        return sum(feasibility_indicators) / len(feasibility_indicators)
    
    def _assess_completeness(self, plan: Dict[str, Any]) -> float:
        """Assess plan completeness"""
        
        required_sections = [
            "architecture", "implementation", "phases", "timeline",
            "resources", "risks", "deliverables", "testing"
        ]
        
        plan_text = str(plan).lower()
        present_sections = sum(1 for section in required_sections if section in plan_text)
        
        return present_sections / len(required_sections)
    
    def _assess_innovation(self, plan: Dict[str, Any]) -> float:
        """Assess innovation and creativity"""
        
        innovation_keywords = [
            "ai", "machine learning", "automation", "optimization",
            "integration", "scalable", "modern", "advanced"
        ]
        
        plan_text = str(plan).lower()
        innovation_indicators = sum(1 for keyword in innovation_keywords if keyword in plan_text)
        
        return min(1.0, innovation_indicators / len(innovation_keywords))
    
    def _assess_resource_efficiency(self, plan: Dict[str, Any]) -> float:
        """Assess resource efficiency"""
        
        efficiency_indicators = [
            "cost" in str(plan).lower(),
            "optimization" in str(plan).lower(),
            "efficient" in str(plan).lower(),
            "scalable" in str(plan).lower()
        ]
        
        return sum(efficiency_indicators) / len(efficiency_indicators)
    
    def _assess_risk_mitigation(self, plan: Dict[str, Any]) -> float:
        """Assess risk mitigation strategies"""
        
        risk_keywords = [
            "risk", "mitigation", "backup", "fallback",
            "contingency", "monitoring", "security"
        ]
        
        plan_text = str(plan).lower()
        risk_indicators = sum(1 for keyword in risk_keywords if keyword in plan_text)
        
        return min(1.0, risk_indicators / len(risk_keywords))
    
    def _assess_clarity(self, plan: Dict[str, Any]) -> float:
        """Assess plan clarity and structure"""
        
        if isinstance(plan, dict):
            structure_score = len(plan.keys()) / 10  # Assume 10 is ideal number of sections
            return min(1.0, structure_score)
        
        return 0.5  # Default for non-structured plans
    
    def generate_refinement_suggestions(self, 
                                      metrics: Dict[str, float],
                                      iteration_number: int) -> List[str]:
        """Generate suggestions for plan refinement"""
        
        suggestions = []
        
        # Check each metric and suggest improvements
        if metrics.get("feasibility", 0) < 0.7:
            suggestions.append("Add more detailed technical feasibility analysis")
            suggestions.append("Include resource availability assessment")
        
        if metrics.get("completeness", 0) < 0.8:
            suggestions.append("Expand on missing planning sections")
            suggestions.append("Add more detailed implementation phases")
        
        if metrics.get("innovation", 0) < 0.6:
            suggestions.append("Consider more innovative approaches and technologies") 
            suggestions.append("Explore cutting-edge solutions in the domain")
        
        if metrics.get("resource_efficiency", 0) < 0.7:
            suggestions.append("Optimize resource allocation and usage")
            suggestions.append("Consider cost-effective alternatives")
        
        if metrics.get("risk_mitigation", 0) < 0.7:
            suggestions.append("Strengthen risk analysis and mitigation strategies")
            suggestions.append("Add contingency planning for critical risks")
        
        if metrics.get("clarity", 0) < 0.8:
            suggestions.append("Improve plan structure and organization")
            suggestions.append("Add clearer documentation and explanations")
        
        # Iteration-specific suggestions
        if iteration_number == 1:
            suggestions.append("Focus on breadth - cover all major aspects")
        elif iteration_number == 2:
            suggestions.append("Focus on depth - add detailed specifications")
        else:
            suggestions.append("Focus on optimization - refine and polish")
        
        return suggestions

class EnhancedPlanningMode:
    """Enhanced planning mode with iteration and refinement"""
    
    def __init__(self, workspace_dir: str = "./enhanced_planning_workspace"):
        self.workspace_dir = Path(workspace_dir)
        self.workspace_dir.mkdir(exist_ok=True)
        
        # Initialize components
        self.deepseek_client = None
        self.mcp_manager = MCPServerManager()
        self.mcp_integration = EnhancedMCPIntegration(self.mcp_manager)
        self.ideation_system = IdeationSystem()
        self.framework_planner = FrameworkPlanner()
        self.evaluator = PlanningEvaluator()
        
        # Session tracking
        self.active_sessions: Dict[str, PlanningSession] = {}
        self.session_history: List[PlanningSession] = []
    
    async def __aenter__(self):
        self.deepseek_client = DeepSeekClient()
        await self.deepseek_client.__aenter__()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.deepseek_client:
            await self.deepseek_client.__aexit__(exc_type, exc_val, exc_tb)
    
    async def start_planning_session(self, 
                                   domain: str,
                                   requirements: Dict[str, Any],
                                   max_iterations: int = 3,
                                   convergence_threshold: float = 0.85) -> str:
        """Start a new enhanced planning session"""
        
        session_id = f"planning_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        logger.info(f"🚀 Starting enhanced planning session: {session_id}")
        logger.info(f"Domain: {domain}")
        logger.info(f"Max iterations: {max_iterations}")
        
        # Start MCP servers
        await self._prepare_planning_infrastructure()
        
        # Initialize session
        session = PlanningSession(
            session_id=session_id,
            domain=domain,
            initial_requirements=requirements,
            iterations=[],
            final_plan={},
            convergence_metrics={},
            session_summary={},
            created_at=datetime.now()
        )
        
        self.active_sessions[session_id] = session
        
        # Execute iterative planning
        await self._execute_iterative_planning(
            session, max_iterations, convergence_threshold
        )
        
        # Finalize session
        await self._finalize_planning_session(session)
        
        return session_id
    
    async def _prepare_planning_infrastructure(self):
        """Prepare planning infrastructure (MCP servers, etc.)"""
        
        logger.info("🔧 Preparing planning infrastructure...")
        
        # Start key MCP servers
        essential_servers = ["filesystem", "git", "search", "planning"]
        
        for server_name in essential_servers:
            if server_name in self.mcp_manager.servers:
                await self.mcp_manager.start_server(server_name)
        
        # Health check
        health = await self.mcp_integration.health_check()
        logger.info(f"Infrastructure status: {health['overall_status']}")
    
    async def _execute_iterative_planning(self, 
                                        session: PlanningSession,
                                        max_iterations: int,
                                        convergence_threshold: float):
        """Execute iterative planning with refinement"""
        
        logger.info(f"🔄 Starting iterative planning for {session.session_id}")
        
        current_context = session.initial_requirements.copy()
        previous_metrics = {}
        
        for iteration_num in range(1, max_iterations + 1):
            logger.info(f"📋 Planning iteration {iteration_num}/{max_iterations}")
            
            # Execute planning iteration
            iteration = await self._execute_planning_iteration(
                session, iteration_num, current_context, previous_metrics
            )
            
            session.iterations.append(iteration)
            
            # Check for convergence
            if iteration.confidence_score >= convergence_threshold:
                logger.info(f"✅ Planning converged at iteration {iteration_num}")
                break
            
            # Prepare for next iteration
            current_context = self._prepare_next_iteration_context(
                current_context, iteration
            )
            previous_metrics = iteration.evaluation_metrics
        
        # Generate final plan
        session.final_plan = await self._synthesize_final_plan(session)
        session.convergence_metrics = self._calculate_convergence_metrics(session)
    
    async def _execute_planning_iteration(self, 
                                        session: PlanningSession,
                                        iteration_num: int,
                                        context: Dict[str, Any],
                                        previous_metrics: Dict[str, float]) -> PlanningIteration:
        """Execute a single planning iteration"""
        
        logger.info(f"🎯 Executing planning iteration {iteration_num}")
        
        tools_used = []
        
        # Step 1: Enhanced ideation (if first iteration)
        if iteration_num == 1:
            logger.info("💡 Generating enhanced ideas...")
            ideas = await self.ideation_system.generate_comprehensive_ideas(
                domain=session.domain,
                target_market=context.get("target_market", "professionals"),
                innovation_level=context.get("innovation_level", "high"),
                count=3
            )
            context["generated_ideas"] = [asdict(idea) for idea in ideas]
            tools_used.append("ideation_system")
        
        # Step 2: DeepSeek-powered planning
        logger.info("🧠 Executing DeepSeek planning...")
        planning_context = PlanningContext(
            domain=session.domain,
            requirements=context,
            constraints=context.get("constraints", {}),
            iteration_count=iteration_num - 1,
            previous_plans=[iter.planning_result for iter in session.iterations]
        )
        
        deepseek_results = await self.deepseek_client.iterative_planning(
            planning_context, max_iterations=1
        )
        tools_used.append("deepseek_planning")
        
        # Step 3: Framework planning integration
        if iteration_num <= 2:  # Only run framework planning in early iterations
            logger.info("🏗️ Executing framework planning...")
            framework_plan = await self.framework_planner.create_comprehensive_plan(
                context, context.get("constraints", {})
            )
            context["framework_plan"] = framework_plan
            tools_used.append("framework_planner")
        
        # Step 4: MCP-enhanced analysis
        logger.info("🔧 Executing MCP-enhanced analysis...")
        mcp_workflow = await self.mcp_integration.execute_planning_workflow(context)
        tools_used.extend(mcp_workflow["tools_used"])
        
        # Step 5: Synthesize iteration result
        planning_result = {
            "iteration": iteration_num,
            "deepseek_planning": deepseek_results[0] if deepseek_results else {},
            "framework_analysis": context.get("framework_plan"),
            "mcp_workflow": mcp_workflow,
            "enhanced_context": context,
            "timestamp": datetime.now().isoformat()
        }
        
        # Step 6: Evaluate iteration
        evaluation_metrics = self.evaluator.evaluate_plan(planning_result, context)
        
        # Step 7: Generate refinement suggestions
        refinement_suggestions = self.evaluator.generate_refinement_suggestions(
            evaluation_metrics, iteration_num
        )
        
        # Calculate confidence score
        confidence_score = evaluation_metrics.get("overall_score", 0.0)
        
        # Apply refinement bonus for later iterations
        if iteration_num > 1 and previous_metrics:
            improvement = confidence_score - previous_metrics.get("overall_score", 0)
            if improvement > 0:
                confidence_score = min(1.0, confidence_score + (improvement * 0.1))
        
        iteration = PlanningIteration(
            iteration_number=iteration_num,
            input_context=context.copy(),
            planning_result=planning_result,
            evaluation_metrics=evaluation_metrics,
            refinement_suggestions=refinement_suggestions,
            confidence_score=confidence_score,
            timestamp=datetime.now(),
            tools_used=tools_used
        )
        
        logger.info(f"✅ Iteration {iteration_num} completed - Score: {confidence_score:.2f}")
        
        return iteration
    
    def _prepare_next_iteration_context(self, 
                                      current_context: Dict[str, Any],
                                      iteration: PlanningIteration) -> Dict[str, Any]:
        """Prepare context for next iteration based on refinement suggestions"""
        
        next_context = current_context.copy()
        
        # Add refinement focus based on suggestions
        next_context["refinement_focus"] = iteration.refinement_suggestions
        next_context["previous_score"] = iteration.confidence_score
        next_context["areas_for_improvement"] = [
            metric for metric, score in iteration.evaluation_metrics.items()
            if score < 0.7
        ]
        
        # Enhance context based on evaluation results
        if iteration.evaluation_metrics.get("feasibility", 0) < 0.7:
            next_context["focus_feasibility"] = True
        
        if iteration.evaluation_metrics.get("completeness", 0) < 0.8:
            next_context["expand_details"] = True
        
        return next_context
    
    async def _synthesize_final_plan(self, session: PlanningSession) -> Dict[str, Any]:
        """Synthesize final plan from all iterations"""
        
        logger.info("🎯 Synthesizing final plan...")
        
        # Get the best iteration
        if not session.iterations:
            return {}
        
        best_iteration = max(session.iterations, key=lambda x: x.confidence_score)
        
        # Use DeepSeek to synthesize final plan
        # Define JSON serializer for datetime objects
        def json_serializer(obj):
            """JSON serializer for objects not serializable by default json code"""
            if isinstance(obj, datetime):
                return obj.isoformat()
            if hasattr(obj, '__dict__'):
                return obj.__dict__
            return str(obj)
        
        synthesis_prompt = f"""
Synthesize a final, comprehensive plan from the following planning iterations:

DOMAIN: {session.domain}
INITIAL REQUIREMENTS: {json.dumps(session.initial_requirements, indent=2, default=json_serializer)}

PLANNING ITERATIONS:
{json.dumps([asdict(iteration) for iteration in session.iterations], indent=2, default=json_serializer)}

BEST ITERATION SCORE: {best_iteration.confidence_score:.2f}

Create a final, optimized plan that:
1. Incorporates the best elements from all iterations
2. Addresses all refinement suggestions
3. Provides clear, actionable guidance
4. Includes comprehensive implementation details
5. Accounts for risks and mitigation strategies

Provide the final plan in a structured format with clear sections.
"""
        
        messages = [{"role": "user", "content": synthesis_prompt}]
        synthesis_response = await self.deepseek_client.chat_completion(
            [{"role": "user", "content": synthesis_prompt}], temperature=0.1
        )
        
        final_plan = {
            "synthesis_result": synthesis_response.content,
            "best_iteration": best_iteration.iteration_number,
            "confidence_score": best_iteration.confidence_score,
            "iterations_processed": len(session.iterations),
            "synthesis_timestamp": datetime.now().isoformat(),
            "all_iterations": [json.loads(json.dumps(asdict(iteration), default=json_serializer)) for iteration in session.iterations]
        }
        
        return final_plan
    
    def _calculate_convergence_metrics(self, session: PlanningSession) -> Dict[str, float]:
        """Calculate convergence metrics for the planning session"""
        
        if len(session.iterations) < 2:
            return {"convergence_rate": 0.0, "improvement_trend": 0.0}
        
        scores = [iteration.confidence_score for iteration in session.iterations]
        
        # Calculate improvement trend
        improvements = [scores[i] - scores[i-1] for i in range(1, len(scores))]
        improvement_trend = sum(improvements) / len(improvements) if improvements else 0
        
        # Calculate convergence rate
        final_score = scores[-1]
        initial_score = scores[0]
        convergence_rate = (final_score - initial_score) / len(session.iterations)
        
        return {
            "convergence_rate": convergence_rate,
            "improvement_trend": improvement_trend,
            "final_score": final_score,
            "score_variance": self._calculate_variance(scores),
            "peak_score": max(scores),
            "iterations_to_peak": scores.index(max(scores)) + 1
        }
    
    def _calculate_variance(self, values: List[float]) -> float:
        """Calculate variance of values"""
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance
    
    async def _finalize_planning_session(self, session: PlanningSession):
        """Finalize and summarize planning session"""
        
        logger.info(f"📋 Finalizing planning session {session.session_id}")
        
        session.completed_at = datetime.now()
        
        # Generate session summary
        session.session_summary = {
            "total_iterations": len(session.iterations),
            "final_confidence": session.final_plan.get("confidence_score", 0),
            "convergence_achieved": session.final_plan.get("confidence_score", 0) >= 0.85,
            "tools_used": list(set(tool for iteration in session.iterations for tool in iteration.tools_used)),
            "planning_duration": (session.completed_at - session.created_at).total_seconds() / 60,
            "key_insights": self._extract_key_insights(session),
            "recommendations": self._generate_final_recommendations(session)
        }
        
        # Save session data
        await self._save_session_data(session)
        
        # Move to history
        self.session_history.append(session)
        if session.session_id in self.active_sessions:
            del self.active_sessions[session.session_id]
        
        logger.info(f"✅ Planning session {session.session_id} completed")
    
    def _extract_key_insights(self, session: PlanningSession) -> List[str]:
        """Extract key insights from planning session"""
        
        insights = []
        
        if session.iterations:
            best_iteration = max(session.iterations, key=lambda x: x.confidence_score)
            insights.append(f"Best planning approach achieved {best_iteration.confidence_score:.1%} confidence")
            
            # Analyze improvement patterns
            scores = [iter.confidence_score for iter in session.iterations]
            if len(scores) > 1:
                total_improvement = scores[-1] - scores[0]
                if total_improvement > 0.1:
                    insights.append(f"Significant improvement of {total_improvement:.1%} through iterations")
                elif total_improvement > 0:
                    insights.append(f"Modest improvement of {total_improvement:.1%} through refinement")
                else:
                    insights.append("Planning quality was consistent across iterations")
        
        return insights
    
    def _generate_final_recommendations(self, session: PlanningSession) -> List[str]:
        """Generate final recommendations based on session results"""
        
        recommendations = []
        
        if session.final_plan.get("confidence_score", 0) >= 0.9:
            recommendations.append("Plan is ready for implementation - proceed with execution")
        elif session.final_plan.get("confidence_score", 0) >= 0.75:
            recommendations.append("Plan is solid - minor refinements may be beneficial")
        else:
            recommendations.append("Plan needs further development - consider additional iteration")
        
        # Tool-specific recommendations
        if session.session_summary.get("tools_used"):
            recommendations.append(f"Leverage {len(session.session_summary['tools_used'])} integrated tools for implementation")
        
        return recommendations
    
    async def _save_session_data(self, session: PlanningSession):
        """Save planning session data"""
        
        session_file = self.workspace_dir / f"{session.session_id}.json"
        
        session_data = {
            "session_id": session.session_id,
            "domain": session.domain,
            "created_at": session.created_at.isoformat(),
            "completed_at": session.completed_at.isoformat() if session.completed_at else None,
            "summary": session.session_summary,
            "convergence_metrics": session.convergence_metrics,
            "iterations_count": len(session.iterations),
            "final_confidence": session.final_plan.get("confidence_score", 0)
        }
        
        def json_serializer(obj):
            """JSON serializer for objects not serializable by default json code"""
            if isinstance(obj, datetime):
                return obj.isoformat()
            if hasattr(obj, '__dict__'):
                return obj.__dict__
            return str(obj)
        
        with open(session_file, 'w') as f:
            json.dump(session_data, f, indent=2, default=json_serializer)
        
        logger.info(f"💾 Session data saved to {session_file}")
    
    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Get status of a planning session"""
        
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            return {
                "status": "active",
                "iterations_completed": len(session.iterations),
                "current_confidence": session.iterations[-1].confidence_score if session.iterations else 0,
                "created_at": session.created_at.isoformat()
            }
        
        # Check history
        for session in self.session_history:
            if session.session_id == session_id:
                return {
                    "status": "completed",
                    "summary": session.session_summary,
                    "final_confidence": session.final_plan.get("confidence_score", 0),
                    "completed_at": session.completed_at.isoformat() if session.completed_at else None
                }
        
        return {"status": "not_found"}
    
    def display_planning_results(self, session_id: str):
        """Display comprehensive planning results"""
        
        session = None
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
        else:
            session = next((s for s in self.session_history if s.session_id == session_id), None)
        
        if not session:
            print(f"❌ Session {session_id} not found")
            return
        
        print("\n" + "="*80)
        print(f"🎯 ENHANCED PLANNING RESULTS: {session.session_id}")
        print("="*80)
        
        print(f"\n📋 Session Overview:")
        print(f"   Domain: {session.domain}")
        print(f"   Created: {session.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        if session.completed_at:
            print(f"   Completed: {session.completed_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Iterations: {len(session.iterations)}")
        
        if session.iterations:
            print(f"\n🔄 Planning Iterations:")
            for iteration in session.iterations:
                print(f"   Iteration {iteration.iteration_number}: {iteration.confidence_score:.1%} confidence")
                print(f"     Tools used: {', '.join(iteration.tools_used)}")
                print(f"     Top suggestions: {'; '.join(iteration.refinement_suggestions[:2])}")
        
        if session.convergence_metrics:
            print(f"\n📊 Convergence Metrics:")
            for metric, value in session.convergence_metrics.items():
                print(f"   {metric.replace('_', ' ').title()}: {value:.3f}")
        
        if session.session_summary:
            print(f"\n📋 Session Summary:")
            summary = session.session_summary
            print(f"   Final Confidence: {summary.get('final_confidence', 0):.1%}")
            print(f"   Convergence Achieved: {'✅ Yes' if summary.get('convergence_achieved') else '❌ No'}")
            print(f"   Planning Duration: {summary.get('planning_duration', 0):.1f} minutes")
            
            if summary.get("key_insights"):
                print(f"   Key Insights:")
                for insight in summary["key_insights"]:
                    print(f"     • {insight}")
            
            if summary.get("recommendations"):
                print(f"   Recommendations:")
                for rec in summary["recommendations"]:
                    print(f"     • {rec}")

async def main():
    """Demo enhanced planning mode"""
    
    print("🚀 Enhanced Planning Mode Demo")
    print("=" * 50)
    
    async with EnhancedPlanningMode() as planning_mode:
        
        # Demo planning session
        domain = "AI-powered development tool"
        requirements = {
            "target_market": "professional developers",
            "expected_users": 5000,
            "key_features": ["code_analysis", "automated_refactoring", "team_collaboration"],
            "innovation_level": "high",
            "constraints": {
                "budget": "medium",
                "timeline": "6 months",
                "team_size": 6
            }
        }
        
        print(f"\n🎯 Starting planning session for: {domain}")
        session_id = await planning_mode.start_planning_session(
            domain=domain,
            requirements=requirements,
            max_iterations=3,
            convergence_threshold=0.85
        )
        
        print(f"\n📊 Planning session completed: {session_id}")
        
        # Display results
        planning_mode.display_planning_results(session_id)
        
        # Get session status
        status = planning_mode.get_session_status(session_id)
        print(f"\n✅ Final status: {status['status']}")

if __name__ == "__main__":
    asyncio.run(main())