"""Synthetic data generator for development and testing.

Generates realistic NHS-style data for LSOA areas including:
- Geographic boundaries (simplified polygons)
- IMD deprivation data
- Census demographic data
- Clinical health data
- Accessibility metrics
"""

import random
from datetime import date, datetime
from decimal import Decimal
from typing import Any
from uuid import uuid4

import numpy as np
from shapely.geometry import Point, Polygon
from sqlalchemy.orm import Session

from app.models import (
    LSOA,
    AccessibilityData,
    ClinicalData,
    DEXModelConfig,
    DemographicData,
    IMDData,
    Organization,
    Resource,
    Team,
    User,
)
from app.core.security import get_password_hash


class SyntheticDataGenerator:
    """Generate synthetic data for HealthEquiRoute development."""

    # London bounding box (approximate)
    LONDON_BOUNDS = {
        "min_lng": -0.5,
        "max_lng": 0.3,
        "min_lat": 51.3,
        "max_lat": 51.7,
    }

    # ICB codes for London
    LONDON_ICBS = [
        ("QMJ", "NHS North East London ICB"),
        ("QMF", "NHS North West London ICB"),
        ("QKK", "NHS South East London ICB"),
        ("QWE", "NHS South West London ICB"),
        ("QM7", "NHS North Central London ICB"),
    ]

    # Local authorities
    LOCAL_AUTHORITIES = [
        ("E09000001", "City of London"),
        ("E09000002", "Barking and Dagenham"),
        ("E09000003", "Barnet"),
        ("E09000004", "Bexley"),
        ("E09000005", "Brent"),
        ("E09000006", "Bromley"),
        ("E09000007", "Camden"),
        ("E09000008", "Croydon"),
        ("E09000009", "Ealing"),
        ("E09000010", "Enfield"),
    ]

    def __init__(self, db: Session):
        self.db = db
        random.seed(42)
        np.random.seed(42)

    def generate_all(self, num_lsoa: int = 100) -> dict[str, int]:
        """Generate all synthetic data."""
        counts = {}

        # Generate organizations and teams first
        counts["organizations"] = self._generate_organizations()
        counts["teams"] = self._generate_teams()
        counts["users"] = self._generate_users()
        counts["resources"] = self._generate_resources()

        # Generate LSOA and related data
        counts["lsoa"] = self._generate_lsoa(num_lsoa)
        counts["imd_data"] = self._generate_imd_data()
        counts["demographic_data"] = self._generate_demographic_data()
        counts["clinical_data"] = self._generate_clinical_data()
        counts["accessibility_data"] = self._generate_accessibility_data()

        # Generate DEX model config
        counts["dex_config"] = self._generate_dex_config()

        self.db.commit()
        return counts

    def _generate_organizations(self) -> int:
        """Generate NHS organizations."""
        orgs = []
        for icb_code, icb_name in self.LONDON_ICBS:
            org = Organization(
                id=uuid4(),
                name=icb_name,
                org_type="ICB",
                ods_code=icb_code,
                settings={"default_visit_duration": 30},
            )
            orgs.append(org)
            self.db.add(org)

        self.db.flush()
        return len(orgs)

    def _generate_teams(self) -> int:
        """Generate healthcare teams."""
        orgs = self.db.query(Organization).all()
        teams = []

        team_types = ["DISTRICT_NURSING", "HEALTH_VISITING", "COMMUNITY_MATRON"]

        for org in orgs:
            for i, team_type in enumerate(team_types):
                # Random base location within London
                lng = random.uniform(self.LONDON_BOUNDS["min_lng"], self.LONDON_BOUNDS["max_lng"])
                lat = random.uniform(self.LONDON_BOUNDS["min_lat"], self.LONDON_BOUNDS["max_lat"])

                team = Team(
                    id=uuid4(),
                    organization_id=org.id,
                    name=f"{org.name.split()[-2]} {team_type.replace('_', ' ').title()} Team",
                    team_type=team_type,
                    base_location=f"SRID=4326;POINT({lng} {lat})",
                    working_hours={
                        "mon": {"start": "08:00", "end": "18:00"},
                        "tue": {"start": "08:00", "end": "18:00"},
                        "wed": {"start": "08:00", "end": "18:00"},
                        "thu": {"start": "08:00", "end": "18:00"},
                        "fri": {"start": "08:00", "end": "17:00"},
                    },
                )
                teams.append(team)
                self.db.add(team)

        self.db.flush()
        return len(teams)

    def _generate_users(self) -> int:
        """Generate system users."""
        orgs = self.db.query(Organization).all()
        teams = self.db.query(Team).all()
        users = []

        # Admin user
        admin = User(
            id=uuid4(),
            email="admin@healthequiroute.nhs.uk",
            password_hash=get_password_hash("admin123"),
            full_name="System Administrator",
            role="ADMIN",
            organization_id=orgs[0].id if orgs else None,
            is_active=True,
        )
        users.append(admin)
        self.db.add(admin)

        # Planner users
        for i, org in enumerate(orgs[:3]):
            planner = User(
                id=uuid4(),
                email=f"planner{i+1}@healthequiroute.nhs.uk",
                password_hash=get_password_hash("planner123"),
                full_name=f"Strategic Planner {i+1}",
                role="PLANNER",
                organization_id=org.id,
                is_active=True,
            )
            users.append(planner)
            self.db.add(planner)

        # Field workers
        for i, team in enumerate(teams[:5]):
            worker = User(
                id=uuid4(),
                email=f"worker{i+1}@healthequiroute.nhs.uk",
                password_hash=get_password_hash("worker123"),
                full_name=f"Community Nurse {i+1}",
                role="FIELD_WORKER",
                organization_id=team.organization_id,
                team_id=team.id,
                is_active=True,
            )
            users.append(worker)
            self.db.add(worker)

        self.db.flush()
        return len(users)

    def _generate_resources(self) -> int:
        """Generate healthcare resources."""
        teams = self.db.query(Team).all()
        resources = []

        skills_pool = [
            ["DIABETES_SPECIALIST"],
            ["PAEDIATRIC"],
            ["MENTAL_HEALTH"],
            ["WOUND_CARE"],
            ["PALLIATIVE_CARE"],
            ["TRANSLATOR_URDU", "TRANSLATOR_BENGALI"],
        ]

        for team in teams:
            # 2-4 resources per team
            num_resources = random.randint(2, 4)
            for i in range(num_resources):
                # Base location near team base
                base_lng = random.uniform(
                    self.LONDON_BOUNDS["min_lng"], self.LONDON_BOUNDS["max_lng"]
                )
                base_lat = random.uniform(
                    self.LONDON_BOUNDS["min_lat"], self.LONDON_BOUNDS["max_lat"]
                )

                resource = Resource(
                    id=uuid4(),
                    team_id=team.id,
                    resource_type="NURSE",
                    name=f"{team.name} - Nurse {i+1}",
                    max_visits_per_day=random.randint(10, 18),
                    skills=random.choice(skills_pool),
                    start_location=f"SRID=4326;POINT({base_lng} {base_lat})",
                    is_available=True,
                )
                resources.append(resource)
                self.db.add(resource)

        self.db.flush()
        return len(resources)

    def _generate_lsoa(self, num_lsoa: int) -> int:
        """Generate LSOA areas with simplified polygons."""
        lsoas = []

        # Grid-based generation for realistic distribution
        grid_size = int(np.ceil(np.sqrt(num_lsoa)))
        lng_step = (self.LONDON_BOUNDS["max_lng"] - self.LONDON_BOUNDS["min_lng"]) / grid_size
        lat_step = (self.LONDON_BOUNDS["max_lat"] - self.LONDON_BOUNDS["min_lat"]) / grid_size

        count = 0
        for i in range(grid_size):
            for j in range(grid_size):
                if count >= num_lsoa:
                    break

                # Base coordinates with some randomness
                base_lng = self.LONDON_BOUNDS["min_lng"] + i * lng_step + random.uniform(0, lng_step * 0.3)
                base_lat = self.LONDON_BOUNDS["min_lat"] + j * lat_step + random.uniform(0, lat_step * 0.3)

                # Create polygon (simplified rectangle with some variation)
                poly_coords = [
                    (base_lng, base_lat),
                    (base_lng + lng_step * 0.8, base_lat + random.uniform(-0.01, 0.01)),
                    (base_lng + lng_step * 0.8 + random.uniform(-0.01, 0.01), base_lat + lat_step * 0.8),
                    (base_lng + random.uniform(-0.01, 0.01), base_lat + lat_step * 0.8),
                    (base_lng, base_lat),
                ]

                polygon = Polygon(poly_coords)
                centroid = polygon.centroid

                # Random ICB and LA assignment
                icb_code, icb_name = random.choice(self.LONDON_ICBS)
                la_code, la_name = random.choice(self.LOCAL_AUTHORITIES)

                lsoa_code = f"E0100{count:04d}"
                lsoa = LSOA(
                    id=uuid4(),
                    lsoa_code=lsoa_code,
                    lsoa_name=f"{la_name} {count:03d}A",
                    local_authority_code=la_code,
                    local_authority_name=la_name,
                    icb_code=icb_code,
                    icb_name=icb_name,
                    geometry=f"SRID=4326;{polygon.wkt}",
                    centroid=f"SRID=4326;POINT({centroid.x} {centroid.y})",
                    area_hectares=Decimal(str(round(random.uniform(20, 100), 2))),
                    population_2021=random.randint(1000, 5000),
                )
                lsoas.append(lsoa)
                self.db.add(lsoa)
                count += 1

        self.db.flush()
        return len(lsoas)

    def _generate_imd_data(self) -> int:
        """Generate IMD deprivation data for all LSOA."""
        lsoas = self.db.query(LSOA).all()
        imd_records = []

        for lsoa in lsoas:
            # Generate realistic IMD distribution (skewed towards middle)
            imd_decile = int(np.clip(np.random.normal(5.5, 2.5), 1, 10))
            imd_rank = random.randint(1, 32844)  # Total LSOA in England
            imd_score = Decimal(str(round(random.uniform(5, 80), 4)))

            imd = IMDData(
                id=uuid4(),
                lsoa_id=lsoa.id,
                data_year=2019,
                imd_rank=imd_rank,
                imd_decile=imd_decile,
                imd_score=imd_score,
                income_score=Decimal(str(round(random.uniform(0, 0.5), 4))),
                employment_score=Decimal(str(round(random.uniform(0, 0.3), 4))),
                education_score=Decimal(str(round(random.uniform(0, 100), 4))),
                health_score=Decimal(str(round(random.uniform(-2, 2), 4))),
                crime_score=Decimal(str(round(random.uniform(-1, 3), 4))),
                housing_score=Decimal(str(round(random.uniform(10, 50), 4))),
                environment_score=Decimal(str(round(random.uniform(10, 80), 4))),
                is_core20=imd_decile <= 2,
            )
            imd_records.append(imd)
            self.db.add(imd)

        self.db.flush()
        return len(imd_records)

    def _generate_demographic_data(self) -> int:
        """Generate Census demographic data for all LSOA."""
        lsoas = self.db.query(LSOA).all()
        demo_records = []

        for lsoa in lsoas:
            total_pop = lsoa.population_2021 or random.randint(1000, 5000)

            # Age distribution
            pct_0_17 = random.uniform(15, 30)
            pct_65_plus = random.uniform(10, 25)
            pct_18_64 = 100 - pct_0_17 - pct_65_plus

            # Ethnicity (varies by area)
            pct_white = random.uniform(40, 95)
            remaining = 100 - pct_white
            pct_asian = remaining * random.uniform(0.2, 0.6)
            pct_black = remaining * random.uniform(0.1, 0.4)
            pct_mixed = remaining * random.uniform(0.05, 0.15)
            pct_other = remaining - pct_asian - pct_black - pct_mixed

            demo = DemographicData(
                id=uuid4(),
                lsoa_id=lsoa.id,
                data_year=2021,
                total_population=total_pop,
                population_0_17=int(total_pop * pct_0_17 / 100),
                population_18_64=int(total_pop * pct_18_64 / 100),
                population_65_plus=int(total_pop * pct_65_plus / 100),
                pct_white=Decimal(str(round(pct_white, 2))),
                pct_asian=Decimal(str(round(pct_asian, 2))),
                pct_black=Decimal(str(round(pct_black, 2))),
                pct_mixed=Decimal(str(round(pct_mixed, 2))),
                pct_other=Decimal(str(round(pct_other, 2))),
                pct_minority=Decimal(str(round(100 - pct_white, 2))),
                pct_english_not_main=Decimal(str(round(random.uniform(5, 40), 2))),
                pct_no_english=Decimal(str(round(random.uniform(0, 10), 2))),
                pct_no_car_household=Decimal(str(round(random.uniform(10, 60), 2))),
                pct_single_parent=Decimal(str(round(random.uniform(5, 25), 2))),
                pct_lone_pensioner=Decimal(str(round(random.uniform(5, 20), 2))),
            )
            demo_records.append(demo)
            self.db.add(demo)

        self.db.flush()
        return len(demo_records)

    def _generate_clinical_data(self) -> int:
        """Generate clinical health data for all LSOA."""
        lsoas = self.db.query(LSOA).all()
        clinical_records = []

        for lsoa in lsoas:
            # Get IMD data to correlate health with deprivation
            imd = self.db.query(IMDData).filter(IMDData.lsoa_id == lsoa.id).first()
            deprivation_factor = 1.0 + (10 - (imd.imd_decile if imd else 5)) * 0.1

            clinical = ClinicalData(
                id=uuid4(),
                lsoa_id=lsoa.id,
                data_period="2023-Q4",
                diabetes_prevalence=Decimal(str(round(random.uniform(50, 120) * deprivation_factor, 2))),
                hypertension_prevalence=Decimal(str(round(random.uniform(100, 200) * deprivation_factor, 2))),
                copd_prevalence=Decimal(str(round(random.uniform(15, 40) * deprivation_factor, 2))),
                asthma_prevalence=Decimal(str(round(random.uniform(50, 100), 2))),
                chd_prevalence=Decimal(str(round(random.uniform(20, 50) * deprivation_factor, 2))),
                stroke_prevalence=Decimal(str(round(random.uniform(10, 30) * deprivation_factor, 2))),
                cancer_prevalence=Decimal(str(round(random.uniform(20, 40), 2))),
                mental_health_prevalence=Decimal(str(round(random.uniform(8, 20) * deprivation_factor, 2))),
                dementia_prevalence=Decimal(str(round(random.uniform(5, 15), 2))),
                emergency_admissions_rate=Decimal(str(round(random.uniform(80, 150) * deprivation_factor, 2))),
                a_and_e_attendance_rate=Decimal(str(round(random.uniform(200, 400) * deprivation_factor, 2))),
                clinical_risk_score=Decimal(str(round(random.uniform(20, 80) * deprivation_factor, 2))),
            )
            clinical_records.append(clinical)
            self.db.add(clinical)

        self.db.flush()
        return len(clinical_records)

    def _generate_accessibility_data(self) -> int:
        """Generate accessibility data for all LSOA."""
        lsoas = self.db.query(LSOA).all()
        access_records = []

        for lsoa in lsoas:
            time_to_gp = random.randint(5, 45)
            time_to_hospital = random.randint(10, 60)
            distance_to_hospital = Decimal(str(round(random.uniform(1, 25), 2)))

            # Determine access category
            if time_to_gp > 30 or float(distance_to_hospital) > 20:
                access_category = "POOR"
            elif time_to_gp > 15 or float(distance_to_hospital) > 10:
                access_category = "MODERATE"
            else:
                access_category = "GOOD"

            access = AccessibilityData(
                id=uuid4(),
                lsoa_id=lsoa.id,
                time_to_nearest_gp=time_to_gp,
                time_to_nearest_hospital=time_to_hospital,
                time_to_nearest_pharmacy=random.randint(3, 20),
                public_transport_accessibility_score=Decimal(str(round(random.uniform(20, 95), 2))),
                distance_to_nearest_gp=Decimal(str(round(random.uniform(0.2, 5), 2))),
                distance_to_nearest_hospital=distance_to_hospital,
                access_category=access_category,
            )
            access_records.append(access)
            self.db.add(access)

        self.db.flush()
        return len(access_records)

    def _generate_dex_config(self) -> int:
        """Generate default DEX model configuration."""
        config = DEXModelConfig(
            id=uuid4(),
            model_version="v1.0",
            is_active=True,
            clinical_weight=Decimal("0.40"),
            social_weight=Decimal("0.35"),
            accessibility_weight=Decimal("0.25"),
            fuzzy_rules={
                "clinical_risk": {
                    "LOW": {"min": 0, "max": 30},
                    "MEDIUM": {"min": 30, "max": 60},
                    "HIGH": {"min": 60, "max": 80},
                    "VERY_HIGH": {"min": 80, "max": 100},
                },
                "social_vulnerability": {
                    "LOW": {"min": 0, "max": 25},
                    "MEDIUM": {"min": 25, "max": 50},
                    "HIGH": {"min": 50, "max": 75},
                    "VERY_HIGH": {"min": 75, "max": 100},
                },
                "accessibility": {
                    "GOOD": {"min": 0, "max": 33},
                    "MODERATE": {"min": 33, "max": 66},
                    "POOR": {"min": 66, "max": 100},
                },
            },
            aggregation_rules={
                "priority_thresholds": {
                    "URGENT": 75,
                    "HIGH": 50,
                    "MEDIUM": 25,
                    "ROUTINE": 0,
                },
                "core20_boost": 10,
                "translator_threshold": 15,
                "specialist_conditions": ["diabetes", "dementia", "mental_health"],
            },
            description="Initial DEX model configuration for MVP",
        )
        self.db.add(config)
        self.db.flush()
        return 1
