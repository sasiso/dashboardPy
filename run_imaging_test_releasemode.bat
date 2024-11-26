REM first cd to release folder and set is current direcotry 
cd /d "C:\Users\satbir.singh\source\repos\MedmontStudio\E300\Tests\si.Tests\x64\SauronRelease"
REM run the test
.\si.Tests.exe --gtest_filter=ImagingPipelineTester.ManualProcessingTest

pause
