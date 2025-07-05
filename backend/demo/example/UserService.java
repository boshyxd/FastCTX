package com.example.demo;

import java.util.ArrayList;
import java.util.List;
import java.sql.*;

public class UserService {
    private DatabaseConnection dbConnection;
    
    public UserService(DatabaseConnection dbConnection) {
        this.dbConnection = dbConnection;
    }
    
    public List<User> getAllUsers() {
        List<User> users = new ArrayList<>();
        String query = "SELECT * FROM users";
        
        try (Statement stmt = dbConnection.getConnection().createStatement();
             ResultSet rs = stmt.executeQuery(query)) {
            
            while (rs.next()) {
                User user = new User(
                    rs.getInt("id"),
                    rs.getString("name"),
                    rs.getString("email"),
                    rs.getBoolean("active")
                );
                users.add(user);
            }
        } catch (SQLException e) {
            System.err.println("Error fetching users: " + e.getMessage());
        }
        
        return users;
    }
    
    public void updateLastLogin(User user) {
        String query = "UPDATE users SET last_login = NOW() WHERE id = ?";
        
        try (PreparedStatement pstmt = dbConnection.getConnection().prepareStatement(query)) {
            pstmt.setInt(1, user.getId());
            pstmt.executeUpdate();
        } catch (SQLException e) {
            System.err.println("Error updating last login: " + e.getMessage());
        }
    }
}
