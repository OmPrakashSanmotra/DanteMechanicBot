response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",   # <-- Yahin change karna hai
            messages=[
                {
                    "role": "system", 
                    "content": "You are Dante, an expert Indian two-wheeler mechanic AI assistant (Ustad Mechanic style, Hinglish expert, specializing in Hero Splendor, HF Deluxe, Honda Activa, Bajaj Pulsar, EV diagnostics, wiring, sensors, and ECU troubleshooting)."
                },
                {
                    "role": "user", 
                    "content": user_query
                }
            ],
            temperature=0.7
        )
