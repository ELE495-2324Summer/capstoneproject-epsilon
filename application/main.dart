import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:async';

void main() {
  runApp(MyWidget());
}

class MyWidget extends StatefulWidget {
  const MyWidget({Key? key}) : super(key: key);

  @override
  _MyWidgetState createState() => _MyWidgetState();
}

class _MyWidgetState extends State<MyWidget> {
  String plateNumber = "";
  int losingPoint = 0;
  String serverIp = '192.168.25.1'; // IP adresi
  final String port = '8765'; // Sabit port numarası
  bool isIpEntered = false; // IP adresi girilip girilmediğini kontrol eden değişken
  bool isParkFound = false; // Plakanın bulunup bulunmadığını kontrol eden değişken
  var isParkStage = false;
  int externalPlateInfo = 0; // Dışarıdan gelen bilgi

  String get parkStatus {
    return isParkStage ? "Park devam ediyor" : "Park etme işlemi bitti";
  }

  Future<void> _sendPlateNumber() async {
    final url = 'http://$serverIp:$port/update_plate';
    final response = await http.post(
      Uri.parse(url),
      headers: <String, String>{
        'Content-Type': 'application/json; charset=UTF-8',
      },
      body: jsonEncode(<String, String>{
        'plate_number': plateNumber,
      }),
    );

    if (response.statusCode == 200) {
      print('Plaka gönderildi: $plateNumber');
    } else {
      print('Plaka gönderimi başarısız oldu');
      setState(() {
        isParkFound = false;
      });
    }
  }

  Future<void> _fetchLosingPoint() async {
    final url = 'http://$serverIp:$port/get_losing_point';
    final response = await http.get(Uri.parse(url));

    if (response.statusCode == 200) {
      setState(() {
        losingPoint = jsonDecode(response.body)['losing_point'];
      });
    } else {
      print('Kaybedilen puan alınamadı');
    }
  }


  Future<void> _fetchExternalPlateInfo() async {
  final url = 'http://$serverIp:$port/get_external_plate';
  final response = await http.get(Uri.parse(url));

  if (response.statusCode == 200) {
    print('Response Body: ${response.body}'); // Debugging
    setState(() {
      externalPlateInfo = jsonDecode(response.body)['detected_plate_number'];
      print('Detected Plate Number: $externalPlateInfo'); // Debugging
      isParkFound = externalPlateInfo.toString() == plateNumber;
    });
  } else {
    print('Dış plaka bilgisi alınamadı');
    setState(() {
      isParkFound = false;
    });
  }
  }

  Future<void> _fetchParkStatus() async {
    final url = 'http://$serverIp:$port/get_park_status';
    final response = await http.get(Uri.parse(url));

    if (response.statusCode == 200) {
      setState(() {
        isParkFound = jsonDecode(response.body)['is_park_found'];
        print('Park status updated: $isParkFound'); // Debugging
      });
    } else {
      print('Park status could not be fetched');
      setState(() {
        isParkFound = false;
      });
    }
  }

  Future<void> _fetchIsParkStage() async {
    final url = 'http://$serverIp:$port/get_is_park_stage';
    final response = await http.get(Uri.parse(url));

    if (response.statusCode == 200) {
      setState(() {
        isParkStage = jsonDecode(response.body)['is_park_stage'];
        print('isParkStage updated: $isParkStage'); // Debugging
      });
    } else {
      print('isParkStage bilgisi alınamadı');
    }
  }

  Future<void> _updateServerConfig(String ip) async {
    final url = 'http://$ip:$port/update_server_config';
    final response = await http.post(
      Uri.parse(url),
      headers: <String, String>{
        'Content-Type': 'application/json; charset=UTF-8',
      },
      body: jsonEncode(<String, String>{
        'server_ip': ip,
        'port': port,
      }),
    );

    if (response.statusCode == 200) {
      print('Sunucu yapılandırması güncellendi');
    } else {
      print('Sunucu yapılandırması güncellemesi başarısız oldu');
    }
  }

  String _getPlateStatus() {
    return plateNumber;
  }

  @override
  void initState() {
    super.initState();
    _fetchLosingPoint();
    _fetchExternalPlateInfo(); // Fetch external plate info on init
    _fetchParkStatus(); // Fetch park status on init
    _fetchIsParkStage(); // Fetch isParkStage on init
    Timer.periodic(Duration(seconds: 1), (Timer t) => _fetchLosingPoint());
    Timer.periodic(Duration(seconds: 1), (Timer t) => _fetchExternalPlateInfo());
    Timer.periodic(Duration(seconds: 1), (Timer t) => _fetchParkStatus()); // Fetch park status periodically
    Timer.periodic(Duration(seconds: 1), (Timer t) => _fetchIsParkStage()); // Fetch isParkStage periodically
  }

  @override
  Widget build(BuildContext context) {
    final double screenHeight = MediaQuery.of(context).size.height;
    return MaterialApp(
      home: Scaffold(
        appBar: PreferredSize(
          preferredSize: Size.fromHeight(kToolbarHeight),
          child: SafeArea(
            child: AppBar(
              title: const Center(
                child: Text("Jetbot Application"),
              ),
              backgroundColor: Colors.lightGreen[400],
            ),
          ),
        ),
        body: SafeArea(
          child: SingleChildScrollView(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.start,
              children: [
                Container(
                  color: Color.fromARGB(255, 171, 183, 181),
                  width: double.infinity,
                  padding: const EdgeInsets.all(10.0),
                  height: screenHeight * 0.15,
                  child: Column(
                    children: [
                      Text(
                        "Sunucu Ayarları",
                        textAlign: TextAlign.center,
                        style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                      ),
                      SizedBox(height: 10),
                      TextField(
                        decoration: InputDecoration(
                          labelText: 'Sunucu IP Adresi',
                          border: OutlineInputBorder(),
                        ),
                        onChanged: (value) {
                          setState(() {
                            serverIp = value;
                          });
                        },
                        onSubmitted: (value) async {
                          setState(() {
                            isIpEntered = true;
                          });
                          await _updateServerConfig(value);
                        },
                      ),
                    ],
                  ),
                ),
                if (isIpEntered) ...[
                  Container(
                    color: Color.fromARGB(255, 200, 200, 200),
                    width: double.infinity,
                    alignment: Alignment.center,
                    padding: const EdgeInsets.all(10.0),
                    height: screenHeight * 0.2,
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text(
                          "JETBOT",
                          textAlign: TextAlign.center,
                          softWrap: true,
                          overflow: TextOverflow.ellipsis,
                        ),
                        SizedBox(height: 10),
                        Image.asset(
                          'images/image_2.jpg',
                          width: 100,
                          height: 100,
                        ),
                      ],
                    ),
                  ),
                  Container(
                    color: Color.fromARGB(255, 171, 183, 181),
                    width: double.infinity,
                    alignment: Alignment.center,
                    padding: const EdgeInsets.all(10.0),
                    height: screenHeight * 0.25, // Height increased to accommodate the new information
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text(
                          "PLAKA BİLGİLERİ",
                          textAlign: TextAlign.center,
                          softWrap: true,
                          overflow: TextOverflow.ellipsis,
                        ),
                        SizedBox(height: 10),
                        TextField(
                          decoration: InputDecoration(
                            labelText: 'Araç Plakası',
                            border: OutlineInputBorder(),
                          ),
                          onChanged: (value) {
                            setState(() {
                              plateNumber = value;
                            });
                          },
                          onSubmitted: (value) {
                            _sendPlateNumber();
                          },
                        ),
                        SizedBox(height: 10),
                        Text(
                          "Plaka: ${_getPlateStatus()}",
                          textAlign: TextAlign.center,
                          softWrap: true,
                          overflow: TextOverflow.ellipsis,
                        ),
                        if (!isParkFound)
                          Text(
                            "Plaka Bulunamadı",
                            textAlign: TextAlign.center,
                            softWrap: true,
                            style: TextStyle(color: Colors.red),
                          ),
                        SizedBox(height: 10), // Space between sections
                        Text(
                          "Okunan Plaka: $externalPlateInfo",
                          textAlign: TextAlign.center,
                          softWrap: true,
                          overflow: TextOverflow.ellipsis,
                          style: TextStyle(color: Colors.blue),
                        ),
                      ],
                    ),
                  ),
                  Container(
                    color: Color.fromARGB(199, 105, 159, 87),
                    width: double.infinity,
                    alignment: Alignment.center,
                    padding: const EdgeInsets.all(10.0),
                    height: screenHeight * 0.15,
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text(
                          "KIRMIZI ÇİZGİ İHLALİ",
                          textAlign: TextAlign.center,
                          softWrap: true,
                          overflow: TextOverflow.ellipsis,
                        ),
                        SizedBox(height: 10),
                        Text(
                          "Kaybedilen Puan: $losingPoint",
                          textAlign: TextAlign.center,
                          softWrap: true,
                        ),
                      ],
                    ),
                  ),
                  Container(
                    color: Color.fromARGB(255, 23, 154, 40),
                    width: double.infinity,
                    alignment: Alignment.center,
                    padding: const EdgeInsets.all(10.0),
                    height: screenHeight * 0.15,
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text(
                          "PARK ETME BİLGİSİ",
                          textAlign: TextAlign.center,
                          softWrap: true,
                          overflow: TextOverflow.ellipsis,
                        ),
                        SizedBox(height: 10),
                        Text(
                          parkStatus,
                          textAlign: TextAlign.center,
                          softWrap: true,
                        ),
                      ],
                    ),
                  ),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }
}
