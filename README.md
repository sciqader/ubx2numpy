# ubx2numpy

This progarm transforms the Ublox data measured by a GPS antenna into a Numpy array. The Python modules required to run this programme are:
~~~
numpy
~~~

~~~
pyubx2
~~~

# a run example:
``` sh
python main_transform_data.py -i Messung_Galileo_GPS.ubx  
```

This can take some time depending on the size of the file. 

At the end, the programm converts the ubx data into a numpy array arranging them in a data container defined as shown in the [this](https://github.com/sciqader/ubx2numpy/blob/main/diagram.pdf) diagram.

#
# author: Qader Dorosti
# email: qader.dorosti@uni-siegen.de
# time: 10:50 21.06.2022

