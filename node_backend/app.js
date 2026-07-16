import express     from "express";
import cors        from "cors";
import dotenv      from "dotenv";
import brainRoutes from "./routes/brainRoutes.js";

dotenv.config();

const app  = express();
const PORT = process.env.PORT || 3001;

app.use(cors());
app.use(express.json());

// Brain module routes
app.use("/api/brain", brainRoutes);

app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});

export default app;
