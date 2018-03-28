const express = require("express");
const graphqlHTTP = require("express-graphql");
const mongoose = require("mongoose");
mongoose.connect("mongodb://localhost/aides-territoires");

// middleware express pour ajouter les headers CORS
const cors = require("cors");
const graphql = require("graphql");
const { buildSchema, GraphQLSchema } = require("graphql");

const helloWorldTypes = require("./services/helloWorld/graphql/helloWorldTypes");
const emailTypes = require("./services/email/graphql/emailTypes");

// our full graphQL schema
const schema = new graphql.GraphQLSchema({
  // "query" type contains all our queries types
  query: new graphql.GraphQLObjectType({
    name: "Query",
    fields: {
      ...helloWorldTypes.queries
    }
  }),
  // "mutation" type contains all our mutations types
  mutation: new graphql.GraphQLObjectType({
    name: "Mutation",
    fields: {
      ...emailTypes.mutations
    }
  })
});

const isDev = process.env.NODE_ENV === "development";
const app = express();
app.use(cors());
// to support JSON-encoded bodies
app.use(express.json());

app.use(
  "/graphql",
  graphqlHTTP({
    schema,
    rootValue: root,
    // always display graphiql explorer for now
    graphiql: true
  })
);

app.use("/", (req, res) => {
  res.json("server is running. Go to /graphql or /api endpoint.");
});

app.listen(4000);
console.log("Running a GraphQL API server at localhost:4000/graphql");
