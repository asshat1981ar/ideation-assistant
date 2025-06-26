package com.ideationassistant.presentation.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material.icons.filled.Schedule
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.navigation.NavController
import com.ideationassistant.domain.models.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun PlanningScreen(navController: NavController) {
    var selectedIdea by remember { mutableStateOf<Idea?>(null) }
    var isPlanning by remember { mutableStateOf(false) }
    var planningSession by remember { mutableStateOf<PlanningSession?>(null) }
    
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        // Header
        Text(
            text = "Smart Planning Studio",
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.Bold
        )
        Text(
            text = "AI-driven iterative planning workflow",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        
        Spacer(modifier = Modifier.height(24.dp))
        
        if (selectedIdea == null) {
            // Idea Selection
            IdeaSelectionSection { idea ->
                selectedIdea = idea
            }
        } else if (planningSession == null && !isPlanning) {
            // Planning Configuration
            PlanningConfigurationSection(
                idea = selectedIdea!!,
                onStartPlanning = { 
                    isPlanning = true
                    // Simulate planning process
                    planningSession = createSamplePlanningSession(selectedIdea!!)
                    isPlanning = false
                }
            )
        } else if (isPlanning) {
            // Planning in Progress
            PlanningProgressSection()
        } else {
            // Planning Results
            PlanningResultsSection(
                session = planningSession!!,
                onCreateProject = {
                    navController.navigate("development")
                }
            )
        }
    }
}

@Composable
fun IdeaSelectionSection(onIdeaSelected: (Idea) -> Unit) {
    Text(
        text = "Select an Idea to Plan",
        style = MaterialTheme.typography.titleLarge,
        fontWeight = FontWeight.Medium
    )
    Spacer(modifier = Modifier.height(16.dp))
    
    LazyColumn(
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        items(getSampleIdeas()) { idea ->
            Card(
                onClick = { onIdeaSelected(idea) },
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(
                    modifier = Modifier.padding(16.dp)
                ) {
                    Text(
                        text = idea.name,
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = idea.description,
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    Row(
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        AssistChip(
                            onClick = { },
                            label = { Text("${(idea.confidenceScore * 100).toInt()}% Confidence") }
                        )
                        AssistChip(
                            onClick = { },
                            label = { Text(idea.domain) }
                        )
                    }
                }
            }
        }
    }
}

@Composable
fun PlanningConfigurationSection(
    idea: Idea,
    onStartPlanning: () -> Unit
) {
    var teamSize by remember { mutableStateOf("4") }
    var timeline by remember { mutableStateOf("3 months") }
    var budget by remember { mutableStateOf("Medium") }
    
    Text(
        text = "Configure Planning",
        style = MaterialTheme.typography.titleLarge,
        fontWeight = FontWeight.Medium
    )
    Spacer(modifier = Modifier.height(16.dp))
    
    Card {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Text(
                text = "Selected Idea: ${idea.name}",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )
            Text(
                text = idea.description,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
    
    Spacer(modifier = Modifier.height(24.dp))
    
    // Configuration Options
    OutlinedTextField(
        value = teamSize,
        onValueChange = { teamSize = it },
        label = { Text("Team Size") },
        modifier = Modifier.fillMaxWidth()
    )
    
    Spacer(modifier = Modifier.height(16.dp))
    
    OutlinedTextField(
        value = timeline,
        onValueChange = { timeline = it },
        label = { Text("Timeline") },
        modifier = Modifier.fillMaxWidth()
    )
    
    Spacer(modifier = Modifier.height(16.dp))
    
    OutlinedTextField(
        value = budget,
        onValueChange = { budget = it },
        label = { Text("Budget") },
        modifier = Modifier.fillMaxWidth()
    )
    
    Spacer(modifier = Modifier.height(24.dp))
    
    Button(
        onClick = onStartPlanning,
        modifier = Modifier.fillMaxWidth()
    ) {
        Icon(Icons.Default.PlayArrow, contentDescription = null)
        Spacer(modifier = Modifier.width(8.dp))
        Text("Start AI Planning")
    }
}

@Composable
fun PlanningProgressSection() {
    Column(
        modifier = Modifier.fillMaxWidth(),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(
            text = "AI Planning in Progress",
            style = MaterialTheme.typography.titleLarge,
            fontWeight = FontWeight.Medium
        )
        Spacer(modifier = Modifier.height(24.dp))
        
        CircularProgressIndicator(
            modifier = Modifier.size(64.dp),
            strokeWidth = 6.dp
        )
        
        Spacer(modifier = Modifier.height(16.dp))
        
        Text(
            text = "Analyzing requirements...",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
    }
}

@Composable
fun PlanningResultsSection(
    session: PlanningSession,
    onCreateProject: () -> Unit
) {
    LazyColumn(
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        item {
            Text(
                text = "Planning Complete",
                style = MaterialTheme.typography.titleLarge,
                fontWeight = FontWeight.Bold
            )
        }
        
        item {
            Card {
                Column(
                    modifier = Modifier.padding(16.dp)
                ) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = "Confidence Score",
                            style = MaterialTheme.typography.titleMedium
                        )
                        Text(
                            text = "${(session.confidenceScore * 100).toInt()}%",
                            style = MaterialTheme.typography.titleLarge,
                            fontWeight = FontWeight.Bold,
                            color = MaterialTheme.colorScheme.primary
                        )
                    }
                    
                    Spacer(modifier = Modifier.height(8.dp))
                    LinearProgressIndicator(
                        progress = session.confidenceScore.toFloat(),
                        modifier = Modifier.fillMaxWidth()
                    )
                }
            }
        }
        
        item {
            Card {
                Column(
                    modifier = Modifier.padding(16.dp)
                ) {
                    Text(
                        text = "Planning Iterations",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold
                    )
                    Spacer(modifier = Modifier.height(12.dp))
                    
                    session.iterations.forEach { iteration ->
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            Text("Iteration ${iteration.iterationNumber}")
                            Text("${(iteration.confidenceScore * 100).toInt()}%")
                        }
                        Spacer(modifier = Modifier.height(4.dp))
                    }
                }
            }
        }
        
        item {
            Button(
                onClick = onCreateProject,
                modifier = Modifier.fillMaxWidth()
            ) {
                Text("Create Project")
            }
        }
    }
}

fun createSamplePlanningSession(idea: Idea): PlanningSession {
    return PlanningSession(
        id = "session_${System.currentTimeMillis()}",
        ideaId = idea.id,
        domain = idea.domain,
        status = PlanningStatus.COMPLETED,
        iterations = listOf(
            PlanningIteration(
                iterationNumber = 1,
                inputContext = "Initial planning",
                planningResult = "Basic architecture defined",
                evaluationMetrics = mapOf("feasibility" to 0.8, "completeness" to 0.7),
                refinementSuggestions = listOf("Add more detail", "Consider scalability"),
                confidenceScore = 0.75
            ),
            PlanningIteration(
                iterationNumber = 2,
                inputContext = "Refined planning",
                planningResult = "Detailed implementation plan",
                evaluationMetrics = mapOf("feasibility" to 0.9, "completeness" to 0.9),
                refinementSuggestions = listOf("Final optimization"),
                confidenceScore = 0.88
            )
        ),
        finalPlan = "Comprehensive development plan with detailed phases",
        confidenceScore = 0.88
    )
}