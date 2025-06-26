package com.ideationassistant.data.local

import androidx.room.*
import com.ideationassistant.data.local.entities.*
import kotlinx.coroutines.flow.Flow

@Dao
interface IdeaDao {
    
    @Query("SELECT * FROM ideas ORDER BY createdAt DESC")
    fun getAllIdeas(): Flow<List<IdeaEntity>>
    
    @Query("SELECT * FROM ideas WHERE id = :id")
    suspend fun getIdeaById(id: String): IdeaEntity?
    
    @Query("SELECT * FROM ideas WHERE domain = :domain ORDER BY confidenceScore DESC")
    fun getIdeasByDomain(domain: String): Flow<List<IdeaEntity>>
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertIdea(idea: IdeaEntity)
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertIdeas(ideas: List<IdeaEntity>)
    
    @Update
    suspend fun updateIdea(idea: IdeaEntity)
    
    @Delete
    suspend fun deleteIdea(idea: IdeaEntity)
    
    @Query("DELETE FROM ideas WHERE id = :id")
    suspend fun deleteIdeaById(id: String)
}

@Dao
interface PlanningDao {
    
    @Query("SELECT * FROM planning_sessions ORDER BY createdAt DESC")
    fun getAllPlanningSessions(): Flow<List<PlanningSessionEntity>>
    
    @Query("SELECT * FROM planning_sessions WHERE id = :id")
    suspend fun getPlanningSessionById(id: String): PlanningSessionEntity?
    
    @Query("SELECT * FROM planning_sessions WHERE ideaId = :ideaId")
    fun getPlanningSessionsByIdeaId(ideaId: String): Flow<List<PlanningSessionEntity>>
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertPlanningSession(session: PlanningSessionEntity)
    
    @Update
    suspend fun updatePlanningSession(session: PlanningSessionEntity)
    
    @Delete
    suspend fun deletePlanningSession(session: PlanningSessionEntity)
}

@Dao
interface ProjectDao {
    
    @Query("SELECT * FROM projects ORDER BY updatedAt DESC")
    fun getAllProjects(): Flow<List<ProjectEntity>>
    
    @Query("SELECT * FROM projects WHERE id = :id")
    suspend fun getProjectById(id: String): ProjectEntity?
    
    @Query("SELECT * FROM projects WHERE ideaId = :ideaId")
    fun getProjectsByIdeaId(ideaId: String): Flow<List<ProjectEntity>>
    
    @Query("SELECT * FROM projects WHERE status = :status")
    fun getProjectsByStatus(status: String): Flow<List<ProjectEntity>>
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertProject(project: ProjectEntity)
    
    @Update
    suspend fun updateProject(project: ProjectEntity)
    
    @Delete
    suspend fun deleteProject(project: ProjectEntity)
}

@Dao
interface UserPreferencesDao {
    
    @Query("SELECT * FROM user_preferences WHERE id = 'default'")
    suspend fun getUserPreferences(): UserPreferencesEntity?
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertUserPreferences(preferences: UserPreferencesEntity)
    
    @Update
    suspend fun updateUserPreferences(preferences: UserPreferencesEntity)
}