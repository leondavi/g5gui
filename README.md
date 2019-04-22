# g5gui
gem5 simulator gui
In early development stage. 
Developed for MinorCPU and RISCV
g5gui is able to run multiple gem5 instances over multiple processes,
It takes care for job scheduling and results saving. 

Requirements: 
Tested on Python version > 3.5 <br/>
tkinter package: ```apt-get install python3-tk```<br/>
Imagetk packages: ``` sudo apt-get install python3-pil python3-pil.imagetk```<br/>
psutil packages: ```sudo pip3 install psutil```<br/>

Running gui open command inside /src directory: ```$: python3 main.py``` 

script.pgp is an example of how to write multiple experiments script file. 
In main menu of g5gui select Script Run button, choose file script and how many 
process to run, then click on run. 

Easier launch add the following lines to the end of ~/.bashrc: <br/>
```G5GUI_FOLDER=$(echo "$HOME/workspace/g5gui" | tr -d '\r')```<br/>
```alias g5gui='cd $G5GUI_FOLDER/src ; python3 main.py'```
