REM We need to build the release version of the project

REM We need to restore working direcotry when we are done with the script, so store curent direcotry in a variable
set current_dir=%cd%


REM first enable visual stuio developer command prompt
REM we are using C:\Program Files\Microsoft Visual Studio\2022\Professional\Common7
call "C:\Program Files\Microsoft Visual Studio\2022\Professional\Common7\Tools\VsDevCmd.bat"

REM change working direcotry to C:\Users\satbir.singh\source\repos\MedmontStudio
cd C:\Users\satbir.singh\source\repos\MedmontStudio


REM now we can build the project, we only build project changed not all, We use maximum number of CPU available
REM we use MedmontStudio.sln in the working directory
REM do not build everything again, only build changed items
msbuild MedmontStudio.sln /t:Build /p:Configuration=SauronRelease /property:Platform=x64 /m

REM restore working directory
cd %current_dir%




