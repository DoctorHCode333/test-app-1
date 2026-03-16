import { combineReducers } from "redux";
import { 
  SET_LOGIN_STATUS,
  SET_USERS_DATA,
  SET_TRANSCRIPT,
  SET_AUDIO_URL,
  SET_DID_DATA,
  SET_DID_LOADING,
  SET_DID_ERROR
 } from "./actions";

const initialState = {
  isLoggedIn: false,
  usersData:{},
  transcript:"",
  audioUrl:"",
  didData: [],
  didLoading: false,
  didError: null
};

////////////////////////////////////////////////////////////////////////////////////////

const loginStatusReducer = (state = initialState.isLoggedIn, action) => {
  switch (action.type) {
    case SET_LOGIN_STATUS:
      return action.payload;
    default:
      return state;
  }
};

const usersDataReducer = (state = initialState.usersData, action) => {
  switch (action.type) {
    case SET_USERS_DATA:
      return {...state,usersData:action.payload};
    default:
      return state;
  }
};
const transcriptDataReducer = (state = initialState.transcript, action) => {
  switch (action.type) {
    case SET_TRANSCRIPT:
      return {...state,transcript:action.payload};
    default:
      return state;
  }
};
const audioUrlReducer = (state = initialState.audioUrl, action) => {
  switch (action.type) {
    case SET_AUDIO_URL:
      return {...state,audioUrl:action.payload};
    default:
      return state;
  }
};

const didDataReducer = (state = initialState.didData, action) => {
  switch (action.type) {
    case SET_DID_DATA:
      return action.payload;
    default:
      return state;
  }
};

const didLoadingReducer = (state = initialState.didLoading, action) => {
  switch (action.type) {
    case SET_DID_LOADING:
      return action.payload;
    default:
      return state;
  }
};

const didErrorReducer = (state = initialState.didError, action) => {
  switch (action.type) {
    case SET_DID_ERROR:
      return action.payload;
    default:
      return state;
  }
};

const rootReducer = combineReducers({
  fetchLoginStatus: loginStatusReducer,
  fetchUsersData: usersDataReducer,
  fetchTranscript: transcriptDataReducer,
  fetchAudioUrl: audioUrlReducer,
  didData: didDataReducer,
  didLoading: didLoadingReducer,
  didError: didErrorReducer,
});

export default rootReducer;
