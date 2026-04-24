import { useState, useRef } from 'react';
import { CameraView, useCameraPermissions } from 'expo-camera';
import { StyleSheet, Text, View, Button, TouchableOpacity, Image } from 'react-native';
// ⚠️ NEW IMPORTS FOR DOWNLOADING!
import * as FileSystem from 'expo-file-system/legacy';
import * as Sharing from 'expo-sharing';

export default function IndexScreen() {
  const [permission, requestPermission] = useCameraPermissions();
  const [photo, setPhoto] = useState<string | null>(null);
  
  // ⚠️ NEW STATE TO HOLD OUR RESULTS
  const [results, setResults] = useState<any>(null); 
  const cameraRef = useRef<any>(null);

  if (!permission) return <View />;
  if (!permission.granted) {
    return (
      <View style={styles.container}>
        <Text style={styles.text}>We need permission to access your camera.</Text>
        <Button onPress={requestPermission} title="Grant Permission" />
      </View>
    );
  }

  const takePicture = async () => {
    if (cameraRef.current) {
      const photoData = await cameraRef.current.takePictureAsync();
      setPhoto(photoData.uri); 
    }
  };

  // -------------------------------------------------------------
  // 🟢 SCREEN 3: THE RESULTS & DOWNLOAD SCREEN
  // -------------------------------------------------------------
  if (results) {
    return (
      <View style={styles.resultsContainer}>
        <Text style={styles.headerText}>Document Scanned!</Text>
        
        <View style={styles.card}>
          {/* ⚠️ FIX: Added '?. ' and fallback text to prevent crashes! */}
          <Text style={styles.detailText}>🏢 Company: {results?.extracted_data?.['Company Name'] || 'Not Found'}</Text>
          <Text style={styles.detailText}>💰 Total: {results?.extracted_data?.['Total'] || 'N/A'}</Text>
          <Text style={styles.detailText}>🖋️ Signature: {results?.extracted_data?.['Status'] || 'Pending'}</Text>

          {/* --- SCANNED GAS TYPES LIST --- */}
          <Text style={{ fontSize: 18, fontWeight: 'bold', marginTop: 15 }}>
            💨 Gas Types:
          </Text>
          {results?.extracted_data?.['Gas Types'] && results.extracted_data['Gas Types'].length > 0 ? (
            results.extracted_data['Gas Types'].map((item: string, index: number) => (
              <View key={`gas-${index}`} style={{ padding: 5, borderBottomWidth: 1, borderColor: '#eee' }}>
                <Text style={{ fontSize: 16 }}>🔵 {item}</Text>
              </View>
            ))
          ) : (
            <Text style={{ fontStyle: 'italic', color: 'gray', marginTop: 5 }}>
              No gas types detected...
            </Text>
          )}

          {/* --- SCANNED CYLINDERS LIST --- */}
          <Text style={{ fontSize: 18, fontWeight: 'bold', marginTop: 15 }}>
            📦 Cylinders:
          </Text>
          {results?.extracted_data?.['Cylinders'] && results.extracted_data['Cylinders'].length > 0 ? (
            results.extracted_data['Cylinders'].map((item: string, index: number) => (
              <View key={`cyl-${index}`} style={{ padding: 5, borderBottomWidth: 1, borderColor: '#eee' }}>
                <Text style={{ fontSize: 16 }}>🟢 SN: {item}</Text>
              </View>
            ))
          ) : (
            <Text style={{ fontStyle: 'italic', color: 'gray', marginTop: 5 }}>
              No cylinders detected...
            </Text>
          )}
        </View>

        <View style={styles.downloadSection}>
          <Button 
            title="📥 Save as PDF" 
            color="#2196F3"
            onPress={async () => {
              try {
                alert("Downloading PDF...");
                // Pointing to your new Python download door!
                const pdfUrl = `https://mahalaxmi-scanner-api.onrender.com/download/${results.pdf_generated}`;
                //@ts-ignore
                const fileUri = FileSystem.documentDirectory + results.pdf_generated;
                
                // Download it to the phone's hidden storage
                const downloadResult = await FileSystem.downloadAsync(pdfUrl, fileUri);
                
                // Open the phone's native "Save/Share" menu!
                await Sharing.shareAsync(downloadResult.uri);
              } catch (e) {
                alert("Error downloading PDF!");
                console.log(e);
              }
            }} 
          />
        </View>
        
        <Button title="Scan Another Document" onPress={() => setResults(null)} color="green" />
      </View>
    );
  }

  // -------------------------------------------------------------
  // 🟡 SCREEN 2: THE PREVIEW & SEND SCREEN
  // -------------------------------------------------------------
  if (photo) {
    return (
      <View style={styles.container}>
        <Image source={{ uri: photo }} style={styles.previewImage} />
        <View style={styles.previewButtons}>
          <Button title="Retake Photo" onPress={() => setPhoto(null)} color="red" />
          <Button 
            title="Send to Python" 
            color="green" 
            onPress={async () => {
              try {
                alert("Sending to laptop...");
                
                const formData = new FormData();
                formData.append('file', {
                  uri: photo,
                  name: 'scanned_document.jpg',
                  type: 'image/jpeg',
                } as any);

                const response = await fetch('https://mahalaxmi-scanner-api.onrender.com/upload/', {
                  method: 'POST',
                  body: formData,
                });

                const result = await response.json();
                
                // ⚠️ INSTEAD OF GOING TO CAMERA, WE GO TO RESULTS SCREEN!
                setResults(result); 
                setPhoto(null); 
                
              } catch (error) {
                alert("Failed to connect. Check your IP address and Wi-Fi!");
                console.log(error);
              }
            }} 
          />
        </View>
      </View>
    );
  }

  // -------------------------------------------------------------
  // 🔴 SCREEN 1: THE CAMERA SCREEN
  // -------------------------------------------------------------
  return (
    <View style={styles.container}>
      <CameraView style={styles.camera} facing="back" ref={cameraRef} />
      <View style={styles.overlay}>
        <View style={styles.targetBox}>
            <Text style={styles.targetText}>Align Document Inside Box</Text>
        </View>
      </View>
      <View style={styles.buttonContainer}>
        <TouchableOpacity style={styles.captureButton} onPress={takePicture}>
          <View style={styles.innerCircle} />
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: 'black' },
  camera: { flex: 1 },
  overlay: { position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, justifyContent: 'center', alignItems: 'center' },
  targetBox: { width: 300, height: 400, borderWidth: 3, borderColor: '#00ff00', borderStyle: 'dashed', justifyContent: 'center', alignItems: 'center' },
  targetText: { color: '#00ff00', fontSize: 16, fontWeight: 'bold', backgroundColor: 'rgba(0,0,0,0.6)', padding: 8, borderRadius: 5 },
  text: { textAlign: 'center', marginBottom: 20, fontSize: 16, paddingHorizontal: 20, color: 'white' },
  buttonContainer: { position: 'absolute', bottom: 40, width: '100%', alignItems: 'center' },
  captureButton: { width: 70, height: 70, borderRadius: 35, backgroundColor: 'rgba(255, 255, 255, 0.5)', justifyContent: 'center', alignItems: 'center' },
  innerCircle: { width: 54, height: 54, borderRadius: 27, backgroundColor: 'white' },
  previewImage: { flex: 1, resizeMode: 'contain' },
  previewButtons: { flexDirection: 'row', justifyContent: 'space-around', padding: 20, backgroundColor: 'black' },
  
  // NEW STYLES FOR THE RESULTS SCREEN
  resultsContainer: { flex: 1, backgroundColor: '#f4f4f4', padding: 20, justifyContent: 'center' },
  headerText: { fontSize: 28, fontWeight: 'bold', textAlign: 'center', marginBottom: 30, color: '#333' },
  card: { backgroundColor: 'white', padding: 20, borderRadius: 10, shadowColor: '#000', shadowOpacity: 0.1, shadowRadius: 5, elevation: 3, marginBottom: 30 },
  detailText: { fontSize: 18, marginBottom: 15, color: '#444' },
  downloadSection: { marginBottom: 20 }
});
