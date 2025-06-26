package com.ideationassistant.core.di

import android.content.Context
import androidx.room.Room
import com.ideationassistant.data.local.IdeationDatabase
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object DatabaseModule {
    
    @Provides
    @Singleton
    fun provideIdeationDatabase(
        @ApplicationContext context: Context
    ): IdeationDatabase {
        return Room.databaseBuilder(
            context.applicationContext,
            IdeationDatabase::class.java,
            "ideation_database"
        ).build()
    }
    
    @Provides
    fun provideIdeaDao(database: IdeationDatabase) = database.ideaDao()
    
    @Provides
    fun providePlanningDao(database: IdeationDatabase) = database.planningDao()
    
    @Provides
    fun provideProjectDao(database: IdeationDatabase) = database.projectDao()
    
    @Provides
    fun provideUserPreferencesDao(database: IdeationDatabase) = database.userPreferencesDao()
}