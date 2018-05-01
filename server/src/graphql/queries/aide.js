const types = require("../types");
const AideModel = require("../../mongoose/Aide");
const {
  GraphQLObjectType,
  GraphQLString,
  GraphQLID,
  GraphQLBoolean,
  GraphQLList,
  GraphQLInt
} = require("graphql");
const { enums, formatEnumForGraphQL } = require("../../enums");
const aideEtapes = formatEnumForGraphQL("searchAideEtapes", enums.AIDE_ETAPES);
const aideStatusPublication = formatEnumForGraphQL(
  "searchAideStatusPublication",
  enums.AIDE_STATUS_PUBLICATION
);
const aideTypes = formatEnumForGraphQL("searchAideTypes", enums.AIDE_TYPES);
const aidePerimetreApplicationTypes = formatEnumForGraphQL(
  "searchAidePerimetreApplicationType",
  enums.AIDE_PERIMETRE_APPLICATION_TYPES
);

module.exports = {
  getAide: {
    type: types.Aide,
    args: {
      id: {
        type: GraphQLID
      }
    },
    resolve: async (_, { id }, context) => {
      return await AideModel.findById(id);
    }
  },
  allAides: {
    type: new GraphQLList(types.Aide),
    args: {
      ...types.Aide._typeConfig.fields()
    },
    resolve: async (_, args = {}, context) => {
      const result = await AideModel.find({}).sort({ updatedAt: "-1" });
      return result;
    }
  },
  searchAides: {
    type: new GraphQLList(types.Aide),
    args: {
      etape: {
        type: new GraphQLList(aideEtapes)
      },
      statusPublication: {
        type: new GraphQLList(aideStatusPublication)
      },
      type: {
        type: new GraphQLList(aideTypes)
      },
      perimetreApplicationType: {
        type: new GraphQLList(aidePerimetreApplicationTypes)
      }
    },
    resolve: async (_, args = {}, context) => {
      const result = await AideModel.find(args);
      return result;
    }
  }
};
