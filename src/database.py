# Build SQLite Database

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, Float, String

class DatabaseManager:
    def __init__(self, db_path="idealfit.db"):
        self.db_path = db_path
        # Placeholder for our database connection object
        self.engine = None
        # Container for table definitions
        self.metadata = MetaData()
        
    def create_engine(self):
        """
        This function creates the connection engine to the SQLite file
        """
        self.engine = create_engine(f"sqlite:///{self.db_path}")
        return self.engine

    def create_tables(self):
        """
        Defines each table (training, ideal, mapping) and creates them in the actual database file
        """
        # If no engine exists
        if self.engine is None:
            self.create_engine()
        
        # 1) 'training' table: x plus y1–y4
        Table(
            "training", self.metadata,
            Column("x", Float, primary_key=True),
            Column("y1", Float),
            Column("y2", Float),
            Column("y3", Float),
            Column("y4", Float),
        )

        # 2) 'ideal' table: x plus y1–y50
        cols = [Column("x", Float, primary_key=True)]
        for i in range(1, 51):
            cols.append(Column(f"y{i}", Float))
        Table("ideal", self.metadata, *cols)
    
        # 3) 'mapping' table: id, x, y, ideal_id, deviation
        Table(
            "mapping", self.metadata,
            Column("id", Integer, primary_key=True, autoincrement=True),
            Column("x", Float),
            Column("y", Float),
            Column("ideal_id", String),
            Column("deviation", Float),
        )
    
        # Create all tables in SQLite file
        self.metadata.create_all(self.engine)
