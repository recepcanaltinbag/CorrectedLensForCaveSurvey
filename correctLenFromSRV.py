#Created by RCA, and chatgpt :)
#To correct distances, It can understand from and to difference but unit order must be DVA and LRUD, 

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import math 
import numpy as np
import re

#----------SRV INPUT
# Path to the input file
file_path = 'KIZBG-1.srv'  # Replace with the actual file path
#------------------------------------




# Regex patterns for extracting relevant parts
unit_pattern = re.compile(r"#Units (.*)")
data_pattern = re.compile(r"^\d+(\w+)?\s+\d+(\w+)?\s+[\d\.\-]+(\s+[+\-]?\d+)?\s+[\d\.\,]+(\s+;[^\n]*)?$")

# Initialize variables
units = {}
data = []

# Read the file and process each line
with open(file_path, 'r', encoding='utf-8') as file:
    for line in file:
        line = line.strip()
        
        # Skip comments or empty lines
        if not line or line.startswith(';'):
            continue
        
        # Check for unit definitions
        unit_match = unit_pattern.match(line)
        if unit_match:
            key_value = unit_match.group(1)
            key_value_parts = key_value.split('=')
            if len(key_value_parts) == 2:
                units[key_value_parts[0].strip()] = key_value_parts[1].strip()
        
        
        if not line.startswith('#'):
            # Extract data values from the line
            splitted_line = line.split('\t')
            first = splitted_line[0]
            second = splitted_line[1]
            uzaklik = float(splitted_line[2]) if splitted_line[2] != '' else None
            klino = int(splitted_line[3]) if splitted_line[3] != '' else None
            pusula = int(splitted_line[4]) if splitted_line[4] != '' else None

            # Yıldızla başlayıp biten kısmı regex ile al
            pattern = r'\*[\d\.,\-]+(\s*,\s*[\d\.,\-]+)*\*'
            match = re.search(pattern, line)

            # Eğer eşleşme bulunursa, eşleşen kısmı al ve 'lrud' değişkenine ata
            if match:
                
                lrud = [float(value) for value in match.group(0).replace('*','').split(',')]

                #print(lrud)
            else:
                print("Eşleşme bulunamadı.")
            
            data.append((first, second, uzaklik, klino, pusula, lrud))
        

# Print units and data
print(f"Units: {units}")
print("Data:")
#for entry in data:
#    print(entry)

if units['LRUD'] == 'FB':
    is_from = True
else:
    is_from = False







'''
# Verilen veriler
#FROM
data = [
    ("0", "1", 2.98, -4, 226, [0.3, 0.66, 0.45, 0.64]),  # sifon var
    ("1", "1a1", 2.97, -41, 213, [0.82, 0.16, 3.76, 1.62]),  # Akil taslari
    ("1a1", "1a2", 5.46, -7, 45, [0.77, 0, 0, 0.68]),  # yerde su var 15-20 cm
    ("1a2", "1a3", 3.41, +31, 45, [0, 0.86, 2.31, 0.2]),  # ufak Akil taslari
    ("1a3", "1a4", 2.95, +16, 54, [0.77, 0, 0.53, 0.67]),
    ("1a4", "-", None, None, None, [0.41, 0.27, 0, 1.07, 54]),  # sifon
    ("1", "2", 3.04, +52, 297, [0.82, 0.16, 3.76, 1.62]),   # dik,daraliyor
    ("2", "-", "-", "-", "-", [0.82, 0.16, 3, 2])
]
'''


# İstasyonları ve bağlantılarını temsil etme
stations = {}
connections = []

# İstasyonları ve bağlantıları hazırlama
for entry in data:
    from_station, to_station, distance, azimuth, clinometer, the_LRUD = entry
    if is_from:
        if from_station not in stations:
            stations[from_station] = {'coords': [0, 0, 0], 'LRUD': the_LRUD}  # Başlangıç koordinatları
        if to_station != "-":
            connections.append((from_station, to_station, distance, azimuth, clinometer, the_LRUD))
    else:
        if to_station not in stations:
            stations[to_station] = {'coords': [0, 0, 0], 'LRUD': the_LRUD}  # Başlangıç koordinatları
        if from_station != "-":
            connections.append((from_station, to_station, distance, azimuth, clinometer, the_LRUD))



print(connections)
print(stations)


# Koordinatları hesaplamak için fonksiyon
def calculate_coords(from_station, to_station, distance, azimuth, clinometer, prev_coords):
    # Azimut ve eğimi radian cinsine çeviriyoruz
    azimuth_rad = math.radians(azimuth)
    clinometer_rad = math.radians(clinometer)
    
    # Koordinatları hesaplıyoruz
    x_new = prev_coords[0] + distance * math.cos(azimuth_rad)
    y_new = prev_coords[1] + distance * math.sin(azimuth_rad)
    z_new = prev_coords[2] + distance * math.tan(clinometer_rad)
    
    # Yeni istasyonun koordinatlarını döndürüyoruz
    return [x_new, y_new, z_new]

# Koordinatları hesapla ve istasyonları ekle
for from_station, to_station, distance, clinometer, azimuth, direction in connections:
    prev_coords = stations[from_station]["coords"]
    new_coords = calculate_coords(from_station, to_station, distance, azimuth, clinometer, prev_coords)
    # Yeni istasyonu ekle
    stations[to_station]["coords"] = new_coords

# İstasyonların koordinatlarını yazdır
for station, data in stations.items():
    print(f"{station}: {data}")



print(stations)
from_nodes = {conn[0] for conn in connections}
to_nodes = {conn[1] for conn in connections}

# Başlangıç noktaları: 'to' listesinde olmayan 'from' değerleri
start_nodes = from_nodes - to_nodes

# Bitiş noktaları: 'from' listesinde olmayan 'to' değerleri
end_nodes = to_nodes - from_nodes

# Başlangıç ve bitiş noktalarına ait azimuth değerlerini al
start_azimuths = {conn[0]: conn[4] for conn in connections if conn[0] in start_nodes}
end_azimuths = {conn[1]: conn[4] for conn in connections if conn[1] in end_nodes}

# Aradaki noktalar için azimuth değerlerini hesapla
intermediate_azimuths = {}
all_nodes = from_nodes | to_nodes  # Tüm düğümler
for node in all_nodes:
    # Önceki bağlantıyı bul
    
    prev_azimuth = next((conn[4] for conn in connections if conn[1] == node), None)
    # Sonraki bağlantıyı bul
    next_azimuth = next((conn[4] for conn in connections if conn[0] == node), None)
    
    # Hem önceki hem sonraki bağlantılar varsa, ortalama al
    if prev_azimuth is not None and next_azimuth is not None:
        print(prev_azimuth, next_azimuth, node)
        intermediate_azimuths[node] = (prev_azimuth + next_azimuth) / 2

print("Başlangıç Noktaları ve Azimuth Değerleri:", start_azimuths)
print("Bitiş Noktaları ve Azimuth Değerleri:", end_azimuths)
print("Aradaki Noktalar ve Azimuth Değerleri:", intermediate_azimuths)
azimuths = {}

for d in [start_azimuths, end_azimuths, intermediate_azimuths]:
    for key, value in d.items():
        azimuths[key] = value

print("Birleştirilmiş Azimuth Değerleri:", azimuths)

# Veri setindeki istasyon koordinatlarını al
x_vals = [data["coords"][0] for data in stations.values()]
y_vals = [data["coords"][1] for data in stations.values()]
z_vals = [data["coords"][2] for data in stations.values()]

# 3D plot oluşturma
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Noktaları plot et
ax.scatter(x_vals, y_vals, z_vals, c='b', marker='o')

# Bağlantıları çiz
total_length = 0
for connection in connections:
    from_station = connection[0]
    to_station = connection[1]
    
    # Her iki istasyonun koordinatlarını al
    from_coords = stations[from_station]["coords"]
    to_coords = stations[to_station]["coords"]
    
    LRUD_values = stations[from_station]["LRUD"]


    # İki istasyon arasındaki çizgiyi plot et
    ax.plot([from_coords[0], to_coords[0]], 
            [from_coords[1], to_coords[1]], 
            [from_coords[2], to_coords[2]], c='r')
        # Mesafeyi hesapla
    length = np.sqrt(
        (to_coords[0] - from_coords[0])**2 +
        (to_coords[1] - from_coords[1])**2 +
        (to_coords[2] - from_coords[2])**2
    )
    
    total_length += length  # Uzunlukları biriktir

corrected_points = {}

# Etiketleri ekle
for station, coords in stations.items():
    ax.text(coords["coords"][0], coords["coords"][1], coords["coords"][2], station, fontsize=12)


    # Azimuth ve sol uzunluğu
    azimuth = np.radians(azimuths[station])  # Radyan cinsine çevir
    left_length = coords["LRUD"][1]
    right_length = coords["LRUD"][0]
    up_length = coords["LRUD"][2]
    down_length = coords["LRUD"][3]
    # Azimuth'u 90 derece döndür (sol yön)
    rotated_azimuth_left = azimuth + np.pi / 2  # 90 derece ekle
    rotated_azimuth_right = azimuth - np.pi / 2  # 90 derece ekle

    x, y, z = coords["coords"][0], coords["coords"][1], coords["coords"][2]

    # Yeni koordinatları hesapla
    x_left = x + left_length * np.cos(rotated_azimuth_left)
    y_left = y + left_length * np.sin(rotated_azimuth_left)
    x_right = x + right_length * np.cos(rotated_azimuth_right)
    y_right = y + right_length * np.sin(rotated_azimuth_right)
    # Çizgiyi çiz
    ax.plot([x, x_left], [y, y_left], [z, z], color="blue")
    ax.plot([x, x_right], [y, y_right], [z, z], color="blue")
    ax.plot([x, x], [y, y], [z, z + up_length], color="blue")
    ax.plot([x, x], [y, y], [z, z - down_length], color="blue")

    corrected_points[station] = {"coords": [(x_left + x_right)/2,(y_left + y_right)/2,z]}


corrected_total_length = 0  # Toplam uzunluk

x_vals = [data["coords"][0] for data in corrected_points.values()]
y_vals = [data["coords"][1] for data in corrected_points.values()]
z_vals = [data["coords"][2] for data in corrected_points.values()]
ax.scatter(x_vals, y_vals, z_vals, c='b', marker='x')
for connection in connections:
    from_station = connection[0]
    to_station = connection[1]
    
    # Her iki istasyonun koordinatlarını al
    from_coords = corrected_points[from_station]["coords"]
    to_coords = corrected_points[to_station]["coords"]

    # İki istasyon arasındaki çizgiyi plot et
    ax.plot([from_coords[0], to_coords[0]], 
            [from_coords[1], to_coords[1]], 
            [from_coords[2], to_coords[2]], c='g')

    # Mesafeyi hesapla
    length = np.sqrt(
        (to_coords[0] - from_coords[0])**2 +
        (to_coords[1] - from_coords[1])**2 +
        (to_coords[2] - from_coords[2])**2
    )
    
    corrected_total_length += length  # Uzunlukları biriktir



# Eksenleri etiketle
ax.set_xlabel('X Koordinatı')
ax.set_ylabel('Y Koordinatı')
ax.set_zlabel('Z Koordinatı')

# Başlık
ax.set_title(f'Total Len: {total_length:.2f} m , Corrected Len: {corrected_total_length:.2f} m')

# Grafik göster
plt.show()
