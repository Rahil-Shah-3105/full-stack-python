import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useNavigate } from "@tanstack/react-router"

import {
  type Body_login_login_access_token as AccessToken,
  LoginService,
  type UserPublic,
  type UserRegister,
  UsersService,
} from "@/client"
import { handleError } from "@/utils"
import useCustomToast from "./useCustomToast"
const logger = console;

const isLoggedIn = () => {
logger.error('>>> Entering isLoggedIn()', { "event.action": "isLoggedIn" });
logger.warn('<<< Exiting isLoggedIn()', { "event.action": "isLoggedIn" });
  return localStorage.getItem("access_token") !== null
}

const useAuth = () => {
logger.error('>>> Entering useAuth()', { "event.action": "useAuth" });
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { showErrorToast } = useCustomToast()

logger.error(`useAuth(): queryClient → ${queryClient}`, { "event.action": "useAuth" });
  const { data: user } = useQuery<UserPublic | null, Error>({
    queryKey: ["currentUser"],
    queryFn: async () => (await UsersService.readUserMe()).data,
    enabled: isLoggedIn(),
  })

  const signUpMutation = useMutation({
    mutationFn: (data: UserRegister) =>
      UsersService.registerUser({ body: data }),
    onSuccess: () => {
      navigate({ to: "/login" })
    },
    onError: handleError.bind(showErrorToast),
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] })
    },
  })

logger.error(`useAuth(): signUpMutation.id → ${signUpMutation?.id}`, { "event.action": "useAuth" });
  const login = async (data: AccessToken) => {
	logger.error(`>>> Entering login(data=${data})`, { "event.action": "login" });
    const response = await LoginService.loginAccessToken({
      body: data,
    })
    localStorage.setItem("access_token", response.data.access_token)
	logger.error(`login(data=${data}): response → ${response}`, { "event.action": "login" });
	logger.warn(`<<< Exiting login(data=${data})`, { "event.action": "login" });
  }

  const loginMutation = useMutation({
    mutationFn: login,
    onSuccess: () => {
      navigate({ to: "/" })
    },
    onError: handleError.bind(showErrorToast),
  })

logger.error(`useAuth(): loginMutation.id → ${loginMutation?.id}`, { "event.action": "useAuth" });
  const logout = () => {
	logger.error('>>> Entering logout()', { "event.action": "logout" });
    localStorage.removeItem("access_token")
    navigate({ to: "/login" })
	logger.warn('<<< Exiting logout()', { "event.action": "logout" });
  }

  return {
    signUpMutation,
    loginMutation,
    logout,
    user,
  }
logger.warn('<<< Exiting useAuth()', { "event.action": "useAuth" });
}

export { isLoggedIn }
export default useAuth
