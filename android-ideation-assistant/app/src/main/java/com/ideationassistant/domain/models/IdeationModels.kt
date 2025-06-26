package com.ideationassistant.domain.models

import android.os.Parcelable
import kotlinx.parcelize.Parcelize
import kotlinx.serialization.Serializable
import java.util.Date

@Parcelize
@Serializable
data class Idea(
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
    val createdAt: Long = System.currentTimeMillis()
) : Parcelable

@Parcelize
@Serializable
data class UserPersona(
    val name: String,
    val description: String,
    val painPoints: List<String>,
    val goals: List<String>
) : Parcelable

@Parcelize
@Serializable
data class MarketInsight(
    val marketSize: String,
    val competitionLevel: String,
    val opportunityScore: Double,
    val trends: List<String>
) : Parcelable

@Parcelize
@Serializable
data class ValidationMetrics(
    val businessViability: Int,
    val technicalFeasibility: Int,
    val marketDemand: Int,
    val overallScore: Double
) : Parcelable

@Parcelize
@Serializable
data class PlanningSession(
    val id: String,
    val ideaId: String,
    val domain: String,
    val status: PlanningStatus,
    val iterations: List<PlanningIteration>,
    val finalPlan: String?,
    val confidenceScore: Double,
    val createdAt: Long = System.currentTimeMillis(),
    val updatedAt: Long = System.currentTimeMillis()
) : Parcelable

@Parcelize
@Serializable
data class PlanningIteration(
    val iterationNumber: Int,
    val inputContext: String,
    val planningResult: String,
    val evaluationMetrics: Map<String, Double>,
    val refinementSuggestions: List<String>,
    val confidenceScore: Double,
    val timestamp: Long = System.currentTimeMillis()
) : Parcelable

@Parcelize
@Serializable
data class Project(
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
    val createdAt: Long = System.currentTimeMillis(),
    val updatedAt: Long = System.currentTimeMillis()
) : Parcelable

@Parcelize
@Serializable
data class ProjectFeature(
    val id: String,
    val name: String,
    val description: String,
    val status: FeatureStatus,
    val priority: Priority,
    val estimatedHours: Int
) : Parcelable

enum class PlanningStatus {
    PENDING, IN_PROGRESS, COMPLETED, FAILED
}

enum class ProjectStatus {
    PLANNING, IN_DEVELOPMENT, TESTING, COMPLETED, PAUSED
}

enum class FeatureStatus {
    PENDING, IN_PROGRESS, COMPLETED, BLOCKED
}

enum class Priority {
    LOW, MEDIUM, HIGH, CRITICAL
}