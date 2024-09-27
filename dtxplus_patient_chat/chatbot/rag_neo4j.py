from neo4j import GraphDatabase

url = "bolt://localhost:7687"
username = "neo4j"
password = "f00bArplusplus"

def store_entities_in_graph(name, extracted_entities):
    # Start building the query
    query = """
    MERGE (p:Person {name: $name})
    """
    
    # Appointment node
    if extracted_entities.appointment:
        query += """
        MERGE (a:Appointment {appointment_date: $appointment_date, appointment_time: $appointment_time})
        MERGE (p)-[:HAS_APPOINTMENT]->(a)
        """
    
    # Medication node
    if extracted_entities.medication:
        query += """
        MERGE (m:Medication {name: $medication_name, frequency: $medication_frequency})
        MERGE (p)-[:TAKES]->(m)
        """
    
    # Weight node
    if extracted_entities.weight:
        query += """
        MERGE (w:Weight {value: $weight})
        MERGE (p)-[:HAS_WEIGHT]->(w)
        """
    
    # Vital Signs node
    if extracted_entities.vital_signs.heart_rate:
        query += """
        MERGE (v:VitalSigns {heart_rate: $heart_rate})
        MERGE (p)-[:HAS_HEART_RATE]->(v)
        """
    
    # Only add Blood Pressure if both systolic and diastolic are not None
    if extracted_entities.vital_signs.blood_pressure:
        systolic = extracted_entities.vital_signs.blood_pressure.systolic
        diastolic = extracted_entities.vital_signs.blood_pressure.diastolic

        if systolic and diastolic:
            query += """
            MERGE (bp:BloodPressure {systolic: $systolic, diastolic: $diastolic})
            MERGE (p)-[:HAS_BLOOD_PRESSURE]->(bp)
            """

    # Lab Tests node
    if extracted_entities.lab_tests:
        if extracted_entities.lab_tests.blood_sugar or extracted_entities.lab_tests.cholesterol:
            query += """
            MERGE (l:LabTest {blood_sugar: $blood_sugar, cholesterol: $cholesterol})
            MERGE (p)-[:HAS_LAB_TEST]->(l)
            """
    
    # Doctor Notes node
    if extracted_entities.doctor_notes:
        query += """
        MERGE (n:DoctorNotes {content: $doctor_notes})
        MERGE (p)-[:RECEIVED_NOTES]->(n)
        """
    
    # Dictionary to store non-null parameters
    params = {
        "name": name,
    }
    
    # Conditionally add parameters for non-null values
    if extracted_entities.appointment:
        params["appointment_date"] = extracted_entities.appointment.date
        params["appointment_time"] = extracted_entities.appointment.time
    
    if extracted_entities.medication:
        params["medication_name"] = extracted_entities.medication.name
        params["medication_frequency"] = extracted_entities.medication.frequency
    
    if extracted_entities.weight:
        params["weight"] = extracted_entities.weight
    
    if extracted_entities.vital_signs:
        params["heart_rate"] = extracted_entities.vital_signs.heart_rate
    
        # Add systolic and diastolic only if they are not None
        if extracted_entities.vital_signs.blood_pressure:
            params["systolic"] = extracted_entities.vital_signs.blood_pressure.systolic
            params["diastolic"] = extracted_entities.vital_signs.blood_pressure.diastolic
    
    if extracted_entities.lab_tests:
        params["blood_sugar"] = extracted_entities.lab_tests.blood_sugar if extracted_entities.lab_tests.blood_sugar else None
        params["cholesterol"] = extracted_entities.lab_tests.cholesterol if extracted_entities.lab_tests.cholesterol else None
    
    if extracted_entities.doctor_notes:
        params["doctor_notes"] = extracted_entities.doctor_notes

    # Execute the query with the constructed params
    with GraphDatabase.driver(url, auth=(username, password)) as driver:
        records, summary, keys = driver.execute_query(query, **params)
    
        print(f"{records=}, {summary=}, {keys=}")