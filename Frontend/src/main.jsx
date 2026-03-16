import App from "./App";
import { connect } from "react-redux";
import { bindActionCreators } from "redux";
import * as actions from "./Redux/actions";

function mapStateToProps(state) {
  return {
    isLoggedIn: state.fetchLoginStatus,
  };
}

function mapDispatchToProps(dispatch) {
  return bindActionCreators({ ...actions }, dispatch);
}

const Main = connect(mapStateToProps, mapDispatchToProps)(App);

export default Main;
