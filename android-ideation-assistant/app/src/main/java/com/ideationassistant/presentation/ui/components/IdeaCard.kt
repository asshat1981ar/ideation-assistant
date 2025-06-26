package com.ideationassistant.presentation.ui.components

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.ideationassistant.domain.models.Idea

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun IdeaCard(
    idea: Idea,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Card(
        onClick = onClick,
        modifier = modifier.fillMaxWidth()
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
                    text = idea.name,
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold
                )
                
                val confidenceColor = when {
                    idea.confidenceScore >= 0.8 -> MaterialTheme.colorScheme.primary
                    idea.confidenceScore >= 0.6 -> MaterialTheme.colorScheme.secondary
                    else -> MaterialTheme.colorScheme.error
                }
                
                Surface(
                    color = confidenceColor.copy(alpha = 0.1f),
                    shape = MaterialTheme.shapes.small
                ) {
                    Text(
                        text = "${(idea.confidenceScore * 100).toInt()}%",
                        modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
                        style = MaterialTheme.typography.labelMedium,
                        color = confidenceColor
                    )
                }
            }
            
            Spacer(modifier = Modifier.height(8.dp))
            
            Text(
                text = idea.description,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            
            Spacer(modifier = Modifier.height(12.dp))
            
            Row(
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                AssistChip(
                    onClick = { },
                    label = { Text(idea.domain) }
                )
                AssistChip(
                    onClick = { },
                    label = { Text(idea.marketSize) }
                )
                AssistChip(
                    onClick = { },
                    label = { Text(idea.innovationLevel) }
                )
            }
        }
    }
}