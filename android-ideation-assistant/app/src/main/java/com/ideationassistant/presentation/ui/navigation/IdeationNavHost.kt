package com.ideationassistant.presentation.ui.navigation

import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Build
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.LightbulbOutline
import androidx.compose.material.icons.filled.Schedule
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.navigation.NavController
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import com.ideationassistant.presentation.ui.screens.*

sealed class Screen(val route: String, val title: String, val icon: ImageVector) {
    object Dashboard : Screen("dashboard", "Dashboard", Icons.Default.Home)
    object Ideation : Screen("ideation", "Ideation", Icons.Default.LightbulbOutline)
    object Planning : Screen("planning", "Planning", Icons.Default.Schedule)
    object Development : Screen("development", "Development", Icons.Default.Build)
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun IdeationNavHost(navController: NavHostController) {
    val items = listOf(
        Screen.Dashboard,
        Screen.Ideation,
        Screen.Planning,
        Screen.Development
    )
    
    Scaffold(
        bottomBar = {
            NavigationBar {
                val navBackStackEntry by navController.currentBackStackEntryAsState()
                val currentDestination = navBackStackEntry?.destination
                
                items.forEach { screen ->
                    NavigationBarItem(
                        icon = { Icon(screen.icon, contentDescription = screen.title) },
                        label = { Text(screen.title) },
                        selected = currentDestination?.route == screen.route,
                        onClick = {
                            navController.navigate(screen.route) {
                                popUpTo(navController.graph.startDestinationId)
                                launchSingleTop = true
                            }
                        }
                    )
                }
            }
        }
    ) { innerPadding ->
        NavHost(
            navController = navController,
            startDestination = Screen.Dashboard.route,
            modifier = Modifier.padding(innerPadding)
        ) {
            composable(Screen.Dashboard.route) {
                DashboardScreen(navController)
            }
            composable(Screen.Ideation.route) {
                IdeationScreen(navController)
            }
            composable(Screen.Planning.route) {
                PlanningScreen(navController)
            }
            composable(Screen.Development.route) {
                DevelopmentScreen(navController)
            }
        }
    }
}