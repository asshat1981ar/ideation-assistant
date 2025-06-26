package com.ideationassistant.data.local

import androidx.room.TypeConverter
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken
import com.ideationassistant.domain.models.*

class Converters {
    
    private val gson = Gson()
    
    @TypeConverter
    fun fromStringList(value: List<String>): String {
        return gson.toJson(value)
    }
    
    @TypeConverter
    fun toStringList(value: String): List<String> {
        val listType = object : TypeToken<List<String>>() {}.type
        return gson.fromJson(value, listType)
    }
    
    @TypeConverter
    fun fromUserPersonaList(value: List<UserPersona>): String {
        return gson.toJson(value)
    }
    
    @TypeConverter
    fun toUserPersonaList(value: String): List<UserPersona> {
        val listType = object : TypeToken<List<UserPersona>>() {}.type
        return gson.fromJson(value, listType)
    }
    
    @TypeConverter
    fun fromMarketInsight(value: MarketInsight): String {
        return gson.toJson(value)
    }
    
    @TypeConverter
    fun toMarketInsight(value: String): MarketInsight {
        return gson.fromJson(value, MarketInsight::class.java)
    }
    
    @TypeConverter
    fun fromValidationMetrics(value: ValidationMetrics): String {
        return gson.toJson(value)
    }
    
    @TypeConverter
    fun toValidationMetrics(value: String): ValidationMetrics {
        return gson.fromJson(value, ValidationMetrics::class.java)
    }
    
    @TypeConverter
    fun fromPlanningIterationList(value: List<PlanningIteration>): String {
        return gson.toJson(value)
    }
    
    @TypeConverter
    fun toPlanningIterationList(value: String): List<PlanningIteration> {
        val listType = object : TypeToken<List<PlanningIteration>>() {}.type
        return gson.fromJson(value, listType)
    }
    
    @TypeConverter
    fun fromProjectFeatureList(value: List<ProjectFeature>): String {
        return gson.toJson(value)
    }
    
    @TypeConverter
    fun toProjectFeatureList(value: String): List<ProjectFeature> {
        val listType = object : TypeToken<List<ProjectFeature>>() {}.type
        return gson.fromJson(value, listType)
    }
    
    @TypeConverter
    fun fromPlanningStatus(value: PlanningStatus): String {
        return value.name
    }
    
    @TypeConverter
    fun toPlanningStatus(value: String): PlanningStatus {
        return PlanningStatus.valueOf(value)
    }
    
    @TypeConverter
    fun fromProjectStatus(value: ProjectStatus): String {
        return value.name
    }
    
    @TypeConverter
    fun toProjectStatus(value: String): ProjectStatus {
        return ProjectStatus.valueOf(value)
    }
    
    @TypeConverter
    fun fromMapStringDouble(value: Map<String, Double>): String {
        return gson.toJson(value)
    }
    
    @TypeConverter
    fun toMapStringDouble(value: String): Map<String, Double> {
        val mapType = object : TypeToken<Map<String, Double>>() {}.type
        return gson.fromJson(value, mapType)
    }
}