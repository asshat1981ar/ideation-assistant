package com.ideationassistant.presentation.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.CheckCircle
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
fun DevelopmentScreen(navController: NavController) {
    var selectedProject by remember { mutableStateOf<Project?>(null) }
    var showCreateProject by remember { mutableStateOf(false) }
    
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
                    text = "Development Hub",
                    style = MaterialTheme.typography.headlineMedium,
                    fontWeight = FontWeight.Bold
                )
                Text(
                    text = "Track and manage your projects",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
            
            FloatingActionButton(
                onClick = { showCreateProject = true },
                modifier = Modifier.size(56.dp)
            ) {
                Icon(Icons.Default.Add, contentDescription = "New Project")
            }
        }
        
        Spacer(modifier = Modifier.height(24.dp))
        
        if (selectedProject == null) {
            // Project List
            ProjectListSection { project ->
                selectedProject = project
            }
        } else {
            // Project Details
            ProjectDetailsSection(
                project = selectedProject!!,
                onBack = { selectedProject = null }
            )
        }
    }
}

@Composable
fun ProjectListSection(onProjectSelected: (Project) -> Unit) {
    val projects = getSampleProjects()
    
    LazyColumn(
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        items(projects) { project ->
            ProjectCard(
                project = project,
                onClick = { onProjectSelected(project) }
            )
        }
    }
}

@Composable
fun ProjectDetailsSection(
    project: Project,
    onBack: () -> Unit
) {
    LazyColumn(
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        item {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = project.name,
                    style = MaterialTheme.typography.headlineSmall,
                    fontWeight = FontWeight.Bold
                )
                TextButton(onClick = onBack) {
                    Text("Back")
                }
            }
        }
        
        item {
            Card {
                Column(
                    modifier = Modifier.padding(16.dp)
                ) {
                    Text(
                        text = "Progress",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    
                    LinearProgressIndicator(
                        progress = project.progress.toFloat(),
                        modifier = Modifier.fillMaxWidth()
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = "${(project.progress * 100).toInt()}% Complete",
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
                        text = "Technology Stack",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    
                    project.techStack.forEach { tech ->
                        Row(
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Icon(
                                Icons.Default.CheckCircle,
                                contentDescription = null,
                                modifier = Modifier.size(16.dp),
                                tint = MaterialTheme.colorScheme.primary
                            )
                            Spacer(modifier = Modifier.width(8.dp))
                            Text(tech)
                        }
                        Spacer(modifier = Modifier.height(4.dp))
                    }
                }
            }
        }
        
        item {
            Card {
                Column(
                    modifier = Modifier.padding(16.dp)
                ) {
                    Text(
                        text = "Project Timeline",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    
                    Row(
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(
                            Icons.Default.Schedule,
                            contentDescription = null,
                            tint = MaterialTheme.colorScheme.primary
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(project.timeline)
                    }
                }
            }
        }
    }
}

@Composable
fun ProjectCard(
    project: Project,
    onClick: () -> Unit
) {
    Card(
        onClick = onClick,
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = project.name,
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold
                )
                
                val statusColor = when (project.status) {
                    ProjectStatus.PLANNING -> MaterialTheme.colorScheme.secondary
                    ProjectStatus.IN_DEVELOPMENT -> MaterialTheme.colorScheme.primary
                    ProjectStatus.TESTING -> MaterialTheme.colorScheme.tertiary
                    ProjectStatus.COMPLETED -> MaterialTheme.colorScheme.primary
                    ProjectStatus.PAUSED -> MaterialTheme.colorScheme.error
                }
                
                AssistChip(
                    onClick = { },
                    label = { Text(project.status.name.replace("_", " ")) },
                    colors = AssistChipDefaults.assistChipColors(
                        leadingIconContentColor = statusColor
                    )
                )
            }
            
            Spacer(modifier = Modifier.height(8.dp))
            
            Text(
                text = project.description,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            
            Spacer(modifier = Modifier.height(12.dp))
            
            LinearProgressIndicator(
                progress = project.progress.toFloat(),
                modifier = Modifier.fillMaxWidth()
            )
            
            Spacer(modifier = Modifier.height(4.dp))
            
            Text(
                text = "${(project.progress * 100).toInt()}% Complete",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}