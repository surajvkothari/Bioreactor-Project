# Bioreactor-Project

## Project Info
This project was part of the ENGF0001 (Engineering Challenges) module in the first year of Computer Science at UCL.
The project was about creating a virtual bioreactor that would be able to provide an optimal environment to help grow the yeast used in manufacturing a TB vaccine.
As we didn't have access to physical components, we used SimAVR to simulate an arduino. 

I helped integrate the separate subsystems (Heating, Stirring, and pH) into one sketch.ino file that would be compiled and executed to run the various components attached to the pins. I also created the GUI using Python's Tkinter. This user interface would be show the actuator data in real-time as well as log the data into a text file. A user could set the setpoints for each subsystem.

The two programs communicated over a two-way serial connection. I used a custom encoding scheme to write data onto the serial. The scheme would allow each program to know what data it was supposed to read and parse.

## Authors
- Suraj Kothari (Computer Science)
- Arslan Aftab (Computer Science)
- Iason Chaimalas (EEE)
- Arnas Vysniauskas (EEE)
