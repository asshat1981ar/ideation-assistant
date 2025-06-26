#!/usr/bin/env python3
"""
DeepSeek API Client
Advanced AI reasoning and planning integration
"""

import asyncio
import json
import os
from typing import Dict, List, Any, Optional, AsyncGenerator
from dataclasses import dataclass, asdict
from datetime import datetime
import aiohttp
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DeepSeekMessage:
    """Message structure for DeepSeek API"""
    role: str
    content: str
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class DeepSeekResponse:
    """Response structure from DeepSeek API"""
    content: str
    usage: Dict[str, int]
    model: str
    timestamp: datetime
    reasoning_depth: int = 0
    confidence_score: float = 0.0

@dataclass
class PlanningContext:
    """Context for planning operations"""
    domain: str
    requirements: Dict[str, Any]
    constraints: Dict[str, Any]
    iteration_count: int = 0
    previous_plans: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.previous_plans is None:
            self.previous_plans = []

class DeepSeekClient:
    """Advanced DeepSeek API client with planning capabilities"""
    
    def __init__(self, api_key: str = None, base_url: str = "https://api.deepseek.com"):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        self.base_url = base_url
        self.session = None
        self.conversation_history = []
        
        if not self.api_key:
            logger.warning("No DeepSeek API key found. Set DEEPSEEK_API_KEY environment variable.")
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def chat_completion(self, 
                             messages: List[DeepSeekMessage],
                             model: str = "deepseek-chat",
                             max_tokens: int = 4000,
                             temperature: float = 0.7,
                             stream: bool = False) -> DeepSeekResponse:
        """Execute chat completion with DeepSeek API"""
        
        if not self.api_key:
            return self._mock_response("Mock response - API key not configured")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": [{"role": msg.role, "content": msg.content} for msg in messages],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": stream
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/v1/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return DeepSeekResponse(
                        content=data["choices"][0]["message"]["content"],
                        usage=data.get("usage", {}),
                        model=data.get("model", model),
                        timestamp=datetime.now(),
                        reasoning_depth=self._analyze_reasoning_depth(data["choices"][0]["message"]["content"]),
                        confidence_score=self._calculate_confidence(data["choices"][0]["message"]["content"])
                    )
                else:
                    logger.error(f"DeepSeek API error: {response.status}")
                    return self._mock_response(f"API Error: {response.status}")
        
        except Exception as e:
            logger.error(f"DeepSeek API request failed: {e}")
            return self._mock_response(f"Connection error: {str(e)}")
    
    async def iterative_planning(self, 
                               context: PlanningContext,
                               max_iterations: int = 3) -> List[Dict[str, Any]]:
        """Perform iterative planning with refinement"""
        
        planning_results = []
        
        for iteration in range(max_iterations):
            logger.info(f"Planning iteration {iteration + 1}/{max_iterations}")
            
            # Build planning prompt
            planning_prompt = self._build_planning_prompt(context, iteration)
            
            # Execute planning
            messages = [DeepSeekMessage(role="user", content=planning_prompt)]
            response = await self.chat_completion(messages, temperature=0.3)
            
            # Parse and evaluate plan
            plan = self._parse_planning_response(response.content)
            plan["iteration"] = iteration + 1
            plan["timestamp"] = datetime.now().isoformat()
            plan["confidence_score"] = response.confidence_score
            plan["reasoning_depth"] = response.reasoning_depth
            
            planning_results.append(plan)
            
            # Update context for next iteration
            context.iteration_count = iteration + 1
            context.previous_plans.append(plan)
            
            # Check if we have converged
            if iteration > 0 and self._check_convergence(planning_results[-2], plan):
                logger.info(f"Planning converged after {iteration + 1} iterations")
                break
        
        return planning_results
    
    async def deep_analysis(self, 
                          subject: str,
                          context: Dict[str, Any],
                          analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """Perform deep analysis using DeepSeek reasoning"""
        
        analysis_prompt = self._build_analysis_prompt(subject, context, analysis_type)
        
        messages = [DeepSeekMessage(role="user", content=analysis_prompt)]
        response = await self.chat_completion(messages, temperature=0.1)
        
        return {
            "subject": subject,
            "analysis_type": analysis_type,
            "content": response.content,
            "confidence_score": response.confidence_score,
            "reasoning_depth": response.reasoning_depth,
            "timestamp": datetime.now().isoformat(),
            "usage": response.usage
        }
    
    async def stream_reasoning(self, 
                             prompt: str,
                             model: str = "deepseek-chat") -> AsyncGenerator[str, None]:
        """Stream reasoning process in real-time"""
        
        if not self.api_key:
            yield "Mock streaming response - API key not configured"
            return
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": True,
            "temperature": 0.7
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/v1/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                async for line in response.content:
                    if line:
                        try:
                            data = json.loads(line.decode('utf-8').strip('data: '))
                            if data.get("choices") and data["choices"][0].get("delta", {}).get("content"):
                                yield data["choices"][0]["delta"]["content"]
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            yield f"Stream error: {str(e)}"
    
    def _build_planning_prompt(self, context: PlanningContext, iteration: int) -> str:
        """Build detailed planning prompt"""
        
        base_prompt = f"""
You are an expert system architect and project planner. Analyze the following requirements and create a comprehensive plan.

DOMAIN: {context.domain}

REQUIREMENTS:
{json.dumps(context.requirements, indent=2)}

CONSTRAINTS:
{json.dumps(context.constraints, indent=2)}

ITERATION: {iteration + 1}
"""
        
        if context.previous_plans:
            base_prompt += f"""
PREVIOUS PLANS:
{json.dumps(context.previous_plans[-1], indent=2)}

REFINEMENT FOCUS:
Based on the previous plan, identify areas for improvement and provide a refined approach.
"""
        
        base_prompt += """
PLANNING REQUIREMENTS:
1. Provide a detailed technical architecture
2. Break down the project into specific phases
3. Identify key risks and mitigation strategies
4. Estimate timeline and resource requirements
5. Suggest technology stack and tools
6. Include validation and testing approaches

RESPONSE FORMAT:
Provide your response as a structured JSON object with the following sections:
- architecture_overview
- technical_stack
- implementation_phases
- risk_analysis
- resource_estimates
- validation_strategy
- key_decisions

Focus on practical, actionable recommendations with clear reasoning.
"""
        
        return base_prompt
    
    def _build_analysis_prompt(self, subject: str, context: Dict[str, Any], analysis_type: str) -> str:
        """Build deep analysis prompt"""
        
        return f"""
Perform a {analysis_type} analysis of: {subject}

CONTEXT:
{json.dumps(context, indent=2)}

ANALYSIS REQUIREMENTS:
1. Identify key components and relationships
2. Analyze strengths, weaknesses, opportunities, and threats
3. Provide actionable insights and recommendations
4. Consider both technical and business perspectives
5. Highlight critical success factors
6. Suggest optimization opportunities

Please provide detailed reasoning for all conclusions and recommendations.
"""
    
    def _parse_planning_response(self, response_content: str) -> Dict[str, Any]:
        """Parse planning response into structured format"""
        
        try:
            # Try to extract JSON from response
            json_start = response_content.find('{')
            json_end = response_content.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_content = response_content[json_start:json_end]
                return json.loads(json_content)
        except json.JSONDecodeError:
            pass
        
        # Fallback to structured text parsing
        return {
            "architecture_overview": self._extract_section(response_content, "architecture"),
            "technical_stack": self._extract_section(response_content, "technical|stack|technology"),
            "implementation_phases": self._extract_section(response_content, "phases|implementation"),
            "risk_analysis": self._extract_section(response_content, "risk|risks"),
            "resource_estimates": self._extract_section(response_content, "resource|estimate|timeline"),
            "validation_strategy": self._extract_section(response_content, "validation|testing"),
            "key_decisions": self._extract_section(response_content, "decision|decisions"),
            "raw_response": response_content
        }
    
    def _extract_section(self, content: str, keywords: str) -> str:
        """Extract section from content based on keywords"""
        
        import re
        
        pattern = rf"(?i).*?({keywords}).*?(?=\n\n|\n[A-Z]|$)"
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            return match.group(0).strip()
        
        return "Section not found"
    
    def _check_convergence(self, prev_plan: Dict[str, Any], current_plan: Dict[str, Any]) -> bool:
        """Check if planning has converged"""
        
        # Simple convergence check based on key similarities
        prev_keys = set(prev_plan.keys())
        current_keys = set(current_plan.keys())
        
        if len(prev_keys.intersection(current_keys)) / len(prev_keys.union(current_keys)) > 0.8:
            return True
        
        return False
    
    def _analyze_reasoning_depth(self, content: str) -> int:
        """Analyze the depth of reasoning in response"""
        
        reasoning_indicators = [
            "because", "therefore", "consequently", "as a result",
            "analysis", "evaluation", "consideration", "assessment",
            "pros and cons", "trade-offs", "implications"
        ]
        
        depth = sum(1 for indicator in reasoning_indicators if indicator.lower() in content.lower())
        return min(10, depth)
    
    def _calculate_confidence(self, content: str) -> float:
        """Calculate confidence score based on content analysis"""
        
        confidence_indicators = {
            "high": ["definitely", "certainly", "clearly", "proven", "established"],
            "medium": ["likely", "probably", "suggests", "indicates", "appears"],
            "low": ["might", "could", "possibly", "perhaps", "uncertain"]
        }
        
        high_count = sum(1 for word in confidence_indicators["high"] if word in content.lower())
        medium_count = sum(1 for word in confidence_indicators["medium"] if word in content.lower())
        low_count = sum(1 for word in confidence_indicators["low"] if word in content.lower())
        
        total_indicators = high_count + medium_count + low_count
        
        if total_indicators == 0:
            return 0.7  # Default confidence
        
        confidence = (high_count * 0.9 + medium_count * 0.6 + low_count * 0.3) / total_indicators
        return round(confidence, 2)
    
    def _mock_response(self, content: str) -> DeepSeekResponse:
        """Create mock response for testing"""
        
        return DeepSeekResponse(
            content=content,
            usage={"prompt_tokens": 100, "completion_tokens": 200, "total_tokens": 300},
            model="deepseek-chat",
            timestamp=datetime.now(),
            reasoning_depth=5,
            confidence_score=0.8
        )

class EnhancedPlanningEngine:
    """Enhanced planning engine with DeepSeek integration"""
    
    def __init__(self, deepseek_client: DeepSeekClient):
        self.deepseek_client = deepseek_client
        self.planning_history = []
    
    async def create_iterative_plan(self, 
                                  domain: str,
                                  requirements: Dict[str, Any],
                                  constraints: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create iterative plan with refinement"""
        
        constraints = constraints or {}
        
        context = PlanningContext(
            domain=domain,
            requirements=requirements,
            constraints=constraints
        )
        
        # Perform iterative planning
        planning_iterations = await self.deepseek_client.iterative_planning(context, max_iterations=3)
        
        # Analyze and synthesize results
        final_plan = await self._synthesize_planning_results(planning_iterations, context)
        
        # Store in history
        self.planning_history.append({
            "context": context,
            "iterations": planning_iterations,
            "final_plan": final_plan,
            "timestamp": datetime.now().isoformat()
        })
        
        return final_plan
    
    async def _synthesize_planning_results(self, 
                                         iterations: List[Dict[str, Any]],
                                         context: PlanningContext) -> Dict[str, Any]:
        """Synthesize multiple planning iterations into final plan"""
        
        synthesis_prompt = f"""
Analyze the following planning iterations and create a final, optimized plan.

PLANNING ITERATIONS:
{json.dumps(iterations, indent=2, default=str)}

CONTEXT:
Domain: {context.domain}
Requirements: {json.dumps(context.requirements, indent=2)}
Constraints: {json.dumps(context.constraints, indent=2)}

SYNTHESIS REQUIREMENTS:
1. Combine the best elements from each iteration
2. Resolve any contradictions or conflicts
3. Ensure consistency and coherence
4. Optimize for feasibility and effectiveness
5. Provide clear implementation guidance

Create a comprehensive final plan that incorporates lessons learned from all iterations.
"""
        
        messages = [DeepSeekMessage(role="user", content=synthesis_prompt)]
        response = await self.deepseek_client.chat_completion(messages, temperature=0.2)
        
        return {
            "final_plan": response.content,
            "iterations_analyzed": len(iterations),
            "confidence_score": response.confidence_score,
            "reasoning_depth": response.reasoning_depth,
            "synthesis_timestamp": datetime.now().isoformat(),
            "raw_iterations": iterations
        }

async def main():
    """Demo DeepSeek integration"""
    
    print("🧠 DeepSeek API Integration Demo")
    print("=" * 50)
    
    async with DeepSeekClient() as client:
        
        # Demo basic chat completion
        print("\n1. Basic Chat Completion:")
        messages = [DeepSeekMessage(role="user", content="Explain the benefits of microservices architecture")]
        response = await client.chat_completion(messages)
        print(f"Response: {response.content[:200]}...")
        print(f"Reasoning Depth: {response.reasoning_depth}")
        print(f"Confidence: {response.confidence_score}")
        
        # Demo iterative planning
        print("\n2. Iterative Planning:")
        context = PlanningContext(
            domain="e-commerce platform",
            requirements={
                "user_base": 10000,
                "features": ["product_catalog", "shopping_cart", "payments"],
                "performance": "high",
                "security": "enterprise"
            },
            constraints={
                "budget": "medium",
                "timeline": "6 months",
                "team_size": 5
            }
        )
        
        planning_results = await client.iterative_planning(context, max_iterations=2)
        print(f"Generated {len(planning_results)} planning iterations")
        
        # Demo enhanced planning engine
        print("\n3. Enhanced Planning Engine:")
        planning_engine = EnhancedPlanningEngine(client)
        final_plan = await planning_engine.create_iterative_plan(
            domain="developer productivity tool",
            requirements={"target_users": 5000, "features": ["code_analysis", "collaboration"]},
            constraints={"budget": "low", "timeline": "3 months"}
        )
        
        print(f"Final plan confidence: {final_plan.get('confidence_score', 'N/A')}")
        print(f"Iterations analyzed: {final_plan.get('iterations_analyzed', 'N/A')}")

if __name__ == "__main__":
    asyncio.run(main())