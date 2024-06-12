import unittest
import io
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
import respx
from httpx import Response
import os

class TestMemeAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create a test database
        cls.SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
        cls.engine = create_engine(cls.SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
        cls.TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=cls.engine)

        # Create the database tables
        Base.metadata.create_all(bind=cls.engine)

        # Override the dependency in the FastAPI app
        def override_get_db():
            try:
                db = cls.TestingSessionLocal()
                yield db
            finally:
                db.close()
        app.dependency_overrides[get_db] = override_get_db

        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        # Drop the test database tables and remove the file
        Base.metadata.drop_all(bind=cls.engine)
        os.remove("./test.db")

    @respx.mock
    def test_create_meme(self):
        mock_route = respx.post("http://media:8001/upload").mock(
            return_value=Response(200, json={"filename": "test_image_url"})
        )
        
        file_content = b"This is a test image content."
        file = io.BytesIO(file_content)
        file.name = "test_image.jpg"
        response = self.client.post(
            "/memes/",
            data={"title": "Test Meme", "description": "A test meme description"},
            files={"image_file": ("test_image.jpg", file, "image/jpeg")},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("id", response.json())
        self.assertEqual(response.json()["title"], "Test Meme")
        self.assertEqual(response.json()["description"], "A test meme description")
        self.assertTrue(mock_route.called)

    @respx.mock
    def test_list_memes(self):
        response = self.client.get("/memes/")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    @respx.mock
    def test_read_meme(self):
        mock_route = respx.post("http://media:8001/upload").mock(
            return_value=Response(200, json={"filename": "test_image_url"})
        )
        
        # First, create a meme to read
        file_content = b"This is a test image content."
        file = io.BytesIO(file_content)
        file.name = "test_image.jpg"
        create_response = self.client.post(
            "/memes/",
            data={"title": "Test Meme", "description": "A test meme description"},
            files={"image_file": ("test_image.jpg", file, "image/jpeg")},
        )
        meme_id = create_response.json()["id"]

        # Then, read the meme
        response = self.client.get(f"/memes/{meme_id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], meme_id)
        self.assertEqual(response.json()["title"], "Test Meme")
        self.assertEqual(response.json()["description"], "A test meme description")
        self.assertTrue(mock_route.called)

    @respx.mock
    def test_update_meme(self):
        mock_route = respx.post("http://media:8001/upload").mock(
            return_value=Response(200, json={"filename": "test_image_url"})
        )
        
        # First, create a meme to update
        file_content = b"This is a test image content."
        file = io.BytesIO(file_content)
        file.name = "test_image.jpg"
        create_response = self.client.post(
            "/memes/",
            data={"title": "Original Title", "description": "Original Description"},
            files={"image_file": ("test_image.jpg", file, "image/jpeg")},
        )
        meme_id = create_response.json()["id"]

        # Then, update the meme
        new_file_content = b"This is updated image content."
        new_file = io.BytesIO(new_file_content)
        new_file.name = "updated_image.jpg"
        response = self.client.put(
            f"/memes/{meme_id}",
            data={"title": "Updated Title", "description": "Updated Description"},
            files={"image_file": ("updated_image.jpg", new_file, "image/jpeg")},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], meme_id)
        self.assertEqual(response.json()["title"], "Updated Title")
        self.assertEqual(response.json()["description"], "Updated Description")
        self.assertTrue(mock_route.called)

    @respx.mock
    def test_delete_meme(self):
        mock_route = respx.post("http://media:8001/upload").mock(
            return_value=Response(200, json={"filename": "test_image_url"})
        )
        
        # First, create a meme to delete
        file_content = b"This is a test image content."
        file = io.BytesIO(file_content)
        file.name = "test_image.jpg"
        create_response = self.client.post(
            "/memes/",
            data={"title": "Meme to Delete", "description": "This meme will be deleted"},
            files={"image_file": ("test_image.jpg", file, "image/jpeg")},
        )
        meme_id = create_response.json()["id"]

        # Then, delete the meme
        response = self.client.delete(f"/memes/{meme_id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], meme_id)

        # Verify that the meme is deleted
        response = self.client.get(f"/memes/{meme_id}")
        self.assertEqual(response.status_code, 404)
        self.assertTrue(mock_route.called)

if __name__ == "__main__":
    unittest.main()
