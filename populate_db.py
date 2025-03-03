from datetime import datetime, timedelta
from database import init_db, get_db
from models.database_models import ClinicalStudy, DataProduct
import random

def populate_sample_data():
    db = next(get_db())

    # Sample status and phases for clinical studies
    statuses = ['Recruiting', 'Active', 'Completed', 'Not yet recruiting']
    phases = ['Phase I', 'Phase II', 'Phase III', 'Phase IV']

    # Generate clinical studies with data products
    for i in range(1, 31):
        start_date = datetime.now() - timedelta(days=random.randint(0, 365))
        study = ClinicalStudy(
            title=f"Cancer Study {i}: {random.choice(['Immunotherapy', 'Targeted Therapy', 'Chemotherapy', 'Radiation'])}",
            description=f"Investigation of novel cancer treatment approach #{i}",
            status=random.choice(statuses),
            phase=random.choice(phases),
            start_date=start_date,
            end_date=start_date + timedelta(days=random.randint(180, 730)),
            relevance_score=round(random.uniform(1.0, 3.5), 2)
        )
        db.add(study)
        db.flush()  # Flush to get the study ID

        # Create a data product for the study
        data_product = DataProduct(
            title=f"Study {i} Data",
            description=f"Clinical data from cancer study #{i}",
            study_id=study.id,
            type=random.choice(['raw', 'processed']),
            format='CSV',
            created_at=datetime.utcnow()
        )
        db.add(data_product)

    db.commit()

if __name__ == "__main__":
    init_db()
    populate_sample_data()
    print("Sample data has been populated successfully!")