package com.example.demo;

import java.util.ArrayList;
import java.util.List;

public class Main {
    private static final String API_KEY = "sk-example-api-key-12345";
    private DatabaseConnection dbConnection;
    private UserService userService;
    
    public static void main(String[] args) {
        Main app = new Main();
        app.initialize();
        app.run();
    }
    
    public void initialize() {
        this.dbConnection = new DatabaseConnection();
        this.userService = new UserService(dbConnection);
        System.out.println("Application initialized");
    }
    
    public void run() {
        List<User> users = userService.getAllUsers();
        for (User user : users) {
            System.out.println("Processing user: " + user.getName());
            processUser(user);
        }
    }
    
    private void processUser(User user) {
        // Process user data
        if (user.isActive()) {
            userService.updateLastLogin(user);
        }
    }
}
