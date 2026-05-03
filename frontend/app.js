const express = require("express");
const axios = require("axios");
const bodyParser = require("body-parser");

const app = express();
const API = "http://localhost:5000";

app.set("view engine", "ejs");
app.use(bodyParser.urlencoded({ extended: true }));

app.get("/", async (req, res) => {
    const members = await axios.get(`${API}/members`);
    const events = await axios.get(`${API}/events`);
    res.render("index", {members: members.data, events: events.data});
});

app.get("/members", async (req, res) => {
    const response = await axios.get(`${API}/members`);
    res.render("members", { members: response.data });
});

app.post("/members", async (req, res) => {
    await axios.post(`${API}/members`, req.body);
    res.redirect("/members");
});

app.get("/events", async (req, res) => {
    const response = await axios.get(`${API}/events`);
    res.render("events", { events: response.data });
});

app.post("/events", async (req, res) => {
    await axios.post(`${API}/events`, req.body);
    res.redirect("/events");
});

app.get("/registrations", async (req, res) => {
    const members = await axios.get(`${API}/members`);
    const events = await axios.get(`${API}/events`);
    res.render("registrations", {members: members.data, events: events.data});
});

app.post("/registrations", async (req, res) => {
    await axios.post(`${API}/registrations`, req.body);
    res.redirect("/registrations");
});

app.listen(3000, () => {
    console.log("Server is running on http://localhost:3000");
});


