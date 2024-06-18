import pandas as pd  # Import the pandas library for data manipulation and analysis

# Read in the data from a CSV file named 'schools.csv'
schools = pd.read_csv("schools.csv")

# Preview the first few rows of the data to understand its structure and contents
schools.head()

# Filter the schools where the average math score is at least 80% of the maximum possible score (assuming 800 is the max score)
best_math_schools_all_data = schools[schools['average_math'] >= 0.8 * 800].sort_values('average_math', ascending=False)

# Select only the school name and average math score columns from the filtered data
best_math_schools = best_math_schools_all_data[['school_name', 'average_math']]

# Print the list of schools with high average math scores
print(best_math_schools)

# Calculate the total SAT score by summing the average math, reading, and writing scores for each school
schools['total_SAT'] = schools['average_math'] + schools['average_reading'] + schools['average_writing']

# Select the top 10 schools based on their total SAT scores and sort them in descending order
top_10_schools = schools[['school_name', 'total_SAT']].sort_values('total_SAT', ascending=False).head(10)

# Print the list of top 10 schools based on their total SAT scores
print(top_10_schools)

# Group the schools by their borough and calculate the mean and standard deviation of the total SAT scores for each group
largest_std_dev = schools.groupby('borough')['total_SAT'].agg(['mean', 'std', 'count']).reset_index()

# Rename the columns for clarity
largest_std_dev.columns = ['borough', 'average_SAT', 'std_SAT', 'num_schools']

# Round the average SAT and standard deviation values to 2 decimal places and sort by the standard deviation in descending order
largest_std_dev = largest_std_dev.round({'average_SAT': 2, 'std_SAT': 2}).sort_values('std_SAT', ascending=False)

# Select the borough with the largest standard deviation in total SAT scores
largest_std_dev = largest_std_dev.head(1)

# Print the borough with the largest variation in total SAT scores
print(largest_std_dev)

# Save the results to CSV files for further use or analysis
best_math_schools.to_csv('best_math_schools.csv', index=False)  # Save without the index column
top_10_schools.to_csv('top_10_schools.csv', index=False)        # Save without the index column
largest_std_dev.to_csv('largest_std_dev.csv', index=False)      # Save without the index column
