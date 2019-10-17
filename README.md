# LoL-Match-Prediction-Nerual-Network
 
 A neural network designed to predict the outcomes of League of Legends (LoL) matches before they even begin.

This project was completed as a part of my AP Research class in my Senior year of highschool, as well as my first serious time working with data scaping from API's and machine learning in some form.

The project involved scraping and formatting ranked games of LoL during patch 9.4, pre-processing the matches, and sending the data into a neural networking, using the Riot Games API to pull match data, Google Sheets to store information on the cloud, and TensorFlow as the neural network basis. More details can be found in the full research paper report found in the repository.

File Descriptions:

Main Scripts\match_data_collector.py - The initial match data collection script.
Main Scripts\match_data_formatter.py - The script that pulled pulled important information out from matches and prepared it as input for the neural network.
Main Scripts\neural_net_example.py - Sample TensorFlow neural network used to base project neural network off of.
Main Scripts\neural_net_input_scraper.py - The script that prepared the outcomes of matches (win or loss) as another input for the neural network.
Main Scripts\neural_net.py - The neural network that was the data was fed into and run.

input_data.txt - Sorted match data as a list to be readied for input.
input_labels.txt - Classifications of a win or loss for the matches found in input_data.txt.
main.py - Temporary file used to run scripts.
README.md - Project README file.
requirements.txt - Versions of API's used.
Robert Marzec AP Research Paper.pdf - Full AP Research Paper submitted to the college board
