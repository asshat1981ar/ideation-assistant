package com.ideationassistant.data.local.entities

import androidx.room.Entity
import androidx.room.PrimaryKey
import com.ideationassistant.domain.models.*

@Entity(tableName = "ideas")
data class IdeaEntity(
    @PrimaryKey
    val id: String,
    val name: String,
    val description: String,
    val domain: String,
    val confidenceScore: Double,
    val marketSize: String,
    val targetMarket: String,
    val innovationLevel: String,
    val features: List<String>,
    val userPersonas: List<UserPersona>,
    val marketInsight: MarketInsight,
    val validationMetrics: ValidationMetrics,
    val futureRoadmap: List<String>,
    val createdAt: Long
)

@Entity(tableName = "planning_sessions")
data class PlanningSessionEntity(
    @PrimaryKey
    val id: String,
    val ideaId: String,
    val domain: String,
    val status: PlanningStatus,
    val iterations: List<PlanningIteration>,
    val finalPlan: String?,
    val confidenceScore: Double,
    val createdAt: Long,
    val updatedAt: Long
)

@Entity(tableName = "projects")
data class ProjectEntity(
    @PrimaryKey
    val id: String,
    val name: String,
    val description: String,
    val ideaId: String,
    val planningSessionId: String?,
    val status: ProjectStatus,
    val progress: Double,
    val techStack: List<String>,
    val features: List<ProjectFeature>,
    val timeline: String,
    val createdAt: Long,
    val updatedAt: Long
)

@Entity(tableName = "user_preferences")
data class UserPreferencesEntity(
    @PrimaryKey
    val id: String = "default",
    val preferredDomains: List<String>,
    val innovationLevel: String,
    val targetMarket: String,
    val techPreferences: List<String>,
    val updatedAt: Long
)