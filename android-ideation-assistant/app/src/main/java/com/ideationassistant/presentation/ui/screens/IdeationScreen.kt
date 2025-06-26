package com.ideationassistant.presentation.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Mic
import androidx.compose.material.icons.filled.Send
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.navigation.NavController
import com.ideationassistant.domain.models.Idea
import com.ideationassistant.presentation.ui.components.IdeaCard

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun IdeationScreen(navController: NavController) {
    var inputText by remember { mutableStateOf("") }
    var selectedDomain by remember { mutableStateOf("") }
    var isGenerating by remember { mutableStateOf(false) }
    var generatedIdeas by remember { mutableStateOf<List<Idea>>(emptyList()) }
    
    val domains = listOf(
        "Developer Tools", "Mobile Apps", "Web Applications", 
        "AI/ML", "Productivity", "Entertainment", "Healthcare", "Finance"
    )
    
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        // Header
        Text(
            text = "AI Ideation Lab",
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.Bold
        )
        Text(
            text = "Generate innovative ideas with AI assistance",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        
        Spacer(modifier = Modifier.height(24.dp))
        
        // Domain Selection
        Text(
            text = "Select Domain",
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Medium
        )
        Spacer(modifier = Modifier.height(8.dp))
        
        LazyColumn(
            modifier = Modifier.height(120.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            items(domains.chunked(2)) { rowDomains ->
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    rowDomains.forEach { domain ->
                        FilterChip(
                            onClick = { selectedDomain = domain },
                            label = { Text(domain) },
                            selected = selectedDomain == domain,
                            modifier = Modifier.weight(1f)
                        )
                    }
                    if (rowDomains.size == 1) {
                        Spacer(modifier = Modifier.weight(1f))
                    }
                }
            }
        }
        
        Spacer(modifier = Modifier.height(24.dp))
        
        // Input Section
        Text(
            text = "Describe Your Vision",
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Medium
        )
        Spacer(modifier = Modifier.height(8.dp))
        
        OutlinedTextField(
            value = inputText,
            onValueChange = { inputText = it },
            modifier = Modifier.fillMaxWidth(),
            placeholder = { Text("Describe your idea, problem, or vision...") },
            minLines = 3,
            maxLines = 5,
            trailingIcon = {
                Row {
                    IconButton(onClick = { /* Voice input */ }) {
                        Icon(Icons.Default.Mic, contentDescription = "Voice Input")
                    }
                }
            }
        )
        
        Spacer(modifier = Modifier.height(16.dp))
        
        // Generate Button
        Button(
            onClick = {
                if (inputText.isNotBlank() && selectedDomain.isNotBlank()) {
                    isGenerating = true
                    // Simulate AI generation
                    generatedIdeas = generateSampleIdeas(selectedDomain, inputText)
                    isGenerating = false
                }
            },
            modifier = Modifier.fillMaxWidth(),
            enabled = inputText.isNotBlank() && selectedDomain.isNotBlank() && !isGenerating
        ) {
            if (isGenerating) {
                CircularProgressIndicator(
                    modifier = Modifier.size(16.dp),
                    strokeWidth = 2.dp
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text("Generating...")
            } else {
                Icon(Icons.Default.Send, contentDescription = null)
                Spacer(modifier = Modifier.width(8.dp))
                Text("Generate Ideas")
            }
        }
        
        Spacer(modifier = Modifier.height(24.dp))
        
        // Generated Ideas
        if (generatedIdeas.isNotEmpty()) {
            Text(
                text = "Generated Ideas",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Medium
            )
            Spacer(modifier = Modifier.height(12.dp))
            
            LazyColumn(
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                items(generatedIdeas) { idea ->
                    IdeaCard(
                        idea = idea,
                        onClick = { 
                            // Navigate to planning with this idea
                            navController.navigate("planning")
                        }
                    )
                }
            }
        }
    }
}

fun generateSampleIdeas(domain: String, input: String): List<Idea> {
    return listOf(
        Idea(
            id = "gen_${System.currentTimeMillis()}",
            name = "$domain Assistant",
            description = "AI-powered assistant for $domain based on: $input",
            domain = domain.lowercase(),
            confidenceScore = 0.87,
            marketSize = "Medium",
            targetMarket = "Professional users",
            innovationLevel = "High",
            features = listOf("AI integration", "User-friendly interface", "Real-time processing"),
            userPersonas = emptyList(),
            marketInsight = com.ideationassistant.domain.models.MarketInsight(
                "Growing", "Medium", 0.8, listOf("AI adoption", "Digital transformation")
            ),
            validationMetrics = com.ideationassistant.domain.models.ValidationMetrics(
                8, 7, 9, 8.0
            ),
            futureRoadmap = listOf("MVP development", "User testing", "Market launch", "Scale")
        )
    )
}