import React, { Component } from "react";
import { graphql, compose } from "react-apollo";
import gql from "graphql-tag";
import AppLoader from "modules/ui-kit/AppLoader";
import PropTypes from "prop-types";
import GraphQLError from "modules/ui-kit/GraphQLError";
import { cleanSearchFilters } from "../lib/search";
import queryString from "qs";

class SearchAideQuery extends Component {
  static propTypes = {
    children: PropTypes.func.isRequired,
    perimetreApplicationType: PropTypes.string,
    perimetreApplicationCode: PropTypes.string,
    etape: PropTypes.array,
    statusPublication: PropTypes.array,
    type: PropTypes.array
  };
  render() {
    if (this.props.data.loading) {
      return <AppLoader />;
    }
    if (this.props.data.error) {
      return <GraphQLError error={this.props.data.error} />;
    }
    return <div>{this.props.children(this.props.data)}</div>;
  }
}

const query = gql`
  query searchAides($filters: searchAidesFilters) {
    results: rechercheAides(filters: $filters) {
      totalNombreAides
      groupesDeResultats {
        type
        label
        nombreAides
        aidesParTypeDeTerritoires {
          type
          label
          aides {
            id
            nom
            createdAt
            updatedAt
            description
            perimetreApplicationType
            perimetreApplicationNom
            perimetreApplicationCode
            etape
            structurePorteuse
            statusPublication
            lien
            type
            beneficiaires
            formeDeDiffusion
            destination
            thematiques
            dateEcheance
            categorieParticuliere
          }
        }
      }
    }
  }
`;

export default compose(
  graphql(query, {
    options: ({ filters }) => {
      filters = cleanSearchFilters(filters);
      return {
        variables: {
          filters
        }
      };
    }
  })
)(SearchAideQuery);