const express = require("express");
const axios = require("axios");
const bodyParser = require("body-parser");
const path = require("path");

const app = express();
const API = "http://127.0.0.1:5000";

app.set("view engine", "ejs");
app.set("views", __dirname);
app.use(bodyParser.urlencoded({ extended: true }));
app.use(express.json());

app.get("/", async (req, res) => {
    try {
        const members = await axios.get(`${API}/members`);
        const events = await axios.get(`${API}/events`);
        res.render("index", { members: members.data, events: events.data });
    } catch (error) {
        res.status(500).send("Error fetching data: " + error.message);
    }
});

app.post("/members", async (req, res) => {
    try {
        await axios.post(`${API}/members`, req.body);
        res.redirect("/");
    } catch (error) { res.status(500).send(error.message); }
});

app.post("/events", async (req, res) => {
    try {
        await axios.post(`${API}/events`, req.body);
        res.redirect("/");
    } catch (error) { res.status(500).send(error.message); }
});

app.post("/registrations", async (req, res) => {
    try {
        await axios.post(`${API}/registrations`, req.body);
        res.redirect("/");
    } catch (error) { res.status(500).send(error.message); }
});

app.listen(3000, () => console.log("Frontend: http://localhost:3000"));
