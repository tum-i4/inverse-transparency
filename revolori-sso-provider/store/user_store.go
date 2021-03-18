package store

import "revolori/user"

// CreateUser writes a given user to the secrets engine 'users'.
func (c Client) CreateUser(user user.User) error {
	secondaryIDs := user.SecondaryIDs
	if secondaryIDs == nil {
		secondaryIDs = map[string][]string{}
	}
	return c.write("users", user.Email, map[string]interface{}{
		"firstName":    user.FirstName,
		"lastName":     user.LastName,
		"password":     user.Password,
		"email":        user.Email,
		"secondaryIDs": secondaryIDs,
	})
}

// GetUser reads a given user from the secrets engine 'users' and returns the user data including the password.
func (c Client) GetUser(email string) (user.User, error) {
	data, err := c.read("users", email)
	if err != nil {
		return user.User{}, err
	}

	var secondaryIDs = make(map[string][]string)
	for key, secondaryIDList := range data["secondaryIDs"].(map[string]interface{}) {
		for _, secondaryID := range secondaryIDList.([]interface{}) {
			secondaryIDs[key] = append(secondaryIDs[key], secondaryID.(string))
		}
	}

	u := user.User{
		Data: user.Data{
			FirstName:    data["firstName"].(string),
			LastName:     data["lastName"].(string),
			Email:        data["email"].(string),
			SecondaryIDs: secondaryIDs,
		},
		Password: data["password"].(string),
	}
	return u, nil
}

// GetUserData reads a given user from the secrets engine 'users' and returns the data without password.
func (c Client) GetUserData(email string) (user.Data, error) {
	u, err := c.GetUser(email)
	if err != nil {
		return user.Data{}, err
	}
	return u.Data, err
}

// GetAllUserData reads all users from the secrets engine 'users' and returns their data without passwords.
func (c Client) GetAllUserData() ([]user.Data, error) {
	data, err := c.getKeys("users")
	if err != nil {
		return nil, err
	}
	keys := data["keys"].([]interface{})
	var users []user.Data
	for _, key := range keys {
		ud, err := c.GetUserData(key.(string))
		if err != nil {
			return nil, err
		}
		users = append(users, ud)
	}
	return users, nil
}

// UpdateUser replaces a user defined by the old email address from the secretes engine 'users' with a new user.
func (c Client) UpdateUser(email string, user user.User) error {
	_, err := c.GetUser(email)
	if err != nil {
		return err
	}

	if err = c.DeleteUser(email); err != nil {
		return err
	}

	return c.CreateUser(user)
}

// DeleteUser deletes a given user from the secrets engine 'users'.
func (c Client) DeleteUser(email string) error {
	return c.delete("users", email)
}
