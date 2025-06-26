package com.ideationassistant.data.local

import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase
import androidx.room.TypeConverters
import android.content.Context
import com.ideationassistant.data.local.entities.*

@Database(
    entities = [
        IdeaEntity::class,
        PlanningSessionEntity::class,
        ProjectEntity::class,
        UserPreferencesEntity::class
    ],
    version = 1,
    exportSchema = false
)
@TypeConverters(Converters::class)
abstract class IdeationDatabase : RoomDatabase() {
    
    abstract fun ideaDao(): IdeaDao
    abstract fun planningDao(): PlanningDao
    abstract fun projectDao(): ProjectDao
    abstract fun userPreferencesDao(): UserPreferencesDao
    
    companion object {
        @Volatile
        private var INSTANCE: IdeationDatabase? = null
        
        fun getDatabase(context: Context): IdeationDatabase {
            return INSTANCE ?: synchronized(this) {
                val instance = Room.databaseBuilder(
                    context.applicationContext,
                    IdeationDatabase::class.java,
                    "ideation_database"
                ).build()
                INSTANCE = instance
                instance
            }
        }
    }
}