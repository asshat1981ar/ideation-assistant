package com.ideationassistant.presentation.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.TrendingUp
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.navigation.NavController
import com.ideationassistant.domain.models.*
import com.ideationassistant.presentation.ui.components.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DashboardScreen(navController: NavController) {
    var selectedTab by remember { mutableStateOf(0) }
    val tabs = listOf("Overview", "Recent Ideas", "Active Projects")
    
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        // Header
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column {
                Text(
                    text = "Ideation Assistant",
                    style = MaterialTheme.typography.headlineMedium,
                    fontWeight = FontWeight.Bold
                )
                Text(
                    text = "AI-Powered Development Workflow",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
            
            FloatingActionButton(
                onClick = { navController.navigate("ideation") },
                modifier = Modifier.size(56.dp)
            ) {
                Icon(Icons.Default.Add, contentDescription = "New Idea")
            }
        }
        
        Spacer(modifier = Modifier.height(24.dp))
        
        // Quick Stats
        LazyRow(
            horizontalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            items(getQuickStats()) { stat ->
                StatCard(stat = stat)
            }
        }
        
        Spacer(modifier = Modifier.height(24.dp))
        
        // Tabs
        TabRow(selectedTabIndex = selectedTab) {
            tabs.forEachIndexed { index, title ->
                Tab(
                    text = { Text(title) },
                    selected = selectedTab == index,
                    onClick = { selectedTab = index }
                )
            }
        }
        
        Spacer(modifier = Modifier.height(16.dp))
        
        // Tab Content
        when (selectedTab) {
            0 -> OverviewContent()
            1 -> RecentIdeasContent()
            2 -> ActiveProjectsContent()
        }
    }
}

@Composable
fun StatCard(stat: QuickStat) {
    Card(
        modifier = Modifier
            .width(120.dp)
            .height(100.dp),
        elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(12.dp),
            verticalArrangement = Arrangement.SpaceBetween
        ) {
            Icon(
                imageVector = stat.icon,
                contentDescription = stat.title,
                tint = MaterialTheme.colorScheme.primary
            )
            Column {
                Text(
                    text = stat.value,
                    style = MaterialTheme.typography.headlineSmall,
                    fontWeight = FontWeight.Bold
                )
                Text(
                    text = stat.title,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
    }
}

@Composable
fun OverviewContent() {
    LazyColumn(
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        item {
            Card {
                Column(
                    modifier = Modifier.padding(16.dp)
                ) {
                    Text(
                        text = "AI Insights",
                        style = MaterialTheme.typography.titleLarge,
                        fontWeight = FontWeight.Bold
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(
                        text = "Based on your recent activity, consider exploring mobile app development with React Native or Flutter for your next project.",
                        style = MaterialTheme.typography.bodyMedium
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
                        text = "Trending Technologies",
                        style = MaterialTheme.typography.titleLarge,
                        fontWeight = FontWeight.Bold
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    
                    val trends = listOf("AI/ML", "Web3", "IoT", "Cloud Native")
                    LazyRow(
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        items(trends) { trend ->
                            SuggestionChip(
                                onClick = { },
                                label = { Text(trend) }
                            )
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun RecentIdeasContent() {
    LazyColumn(
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        items(getSampleIdeas()) { idea ->
            IdeaCard(idea = idea, onClick = { })
        }
    }
}

@Composable
fun ActiveProjectsContent() {
    LazyColumn(
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        items(getSampleProjects()) { project ->
            ProjectCard(project = project, onClick = { })
        }
    }
}

// Sample data functions
fun getQuickStats(): List<QuickStat> {
    return listOf(
        QuickStat("12", "Ideas", Icons.Default.TrendingUp),
        QuickStat("5", "Projects", Icons.Default.TrendingUp),
        QuickStat("3", "Active", Icons.Default.TrendingUp),
        QuickStat("85%", "Success", Icons.Default.TrendingUp)
    )
}

fun getSampleIdeas(): List<Idea> {
    return listOf(
        Idea(
            id = "1",
            name = "Smart Code Reviewer",
            description = "AI-powered code review assistant",
            domain = "developer tools",
            confidenceScore = 0.92,
            marketSize = "Medium",
            targetMarket = "Professional developers",
            innovationLevel = "High",
            features = listOf("Code analysis", "Automated suggestions", "Team integration"),
            userPersonas = emptyList(),
            marketInsight = MarketInsight("Growing", "Medium", 0.8, listOf("AI adoption")),
            validationMetrics = ValidationMetrics(8, 9, 7, 8.0),
            futureRoadmap = listOf("MVP development", "Beta testing", "Market launch")
        )
    )
}

fun getSampleProjects(): List<Project> {
    return listOf(
        Project(
            id = "1",
            name = "Task Management App",
            description = "Modern task management with AI features",
            ideaId = "1",
            planningSessionId = "session1",
            status = ProjectStatus.IN_DEVELOPMENT,
            progress = 0.65,
            techStack = listOf("React Native", "Node.js", "MongoDB"),
            features = emptyList(),
            timeline = "3 months"
        )
    )
}

data class QuickStat(
    val value: String,
    val title: String,
    val icon: androidx.compose.ui.graphics.vector.ImageVector
)