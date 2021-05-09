import { CircularProgress } from "@material-ui/core";
import Markdown from "components/Markdown";
import { Error as GrpcError } from "grpc-web";
import { GetTermsOfServiceRes } from "pb/resources_pb";
import { useQuery } from "react-query";
import { service } from "service";
import makeStyles from "utils/makeStyles";

const useStyles = makeStyles((theme) => ({
  root: {
    maxWidth: theme.breakpoints.values.lg,
    margin: "0 auto",
    padding: theme.spacing(2),
  },
}));

export default function TOS() {
  const classes = useStyles();
  const { data, error, isLoading } = useQuery<
    GetTermsOfServiceRes.AsObject,
    GrpcError
  >({
    queryKey: "tos",
    queryFn: () => service.resources.getTermsOfService(),
  });

  if (error) {
    // Re-throw error to trigger error boundary to encourage user to report it
    // if they can't see the terms
    throw error;
  }

  return isLoading ? (
    <CircularProgress />
  ) : data ? (
    <Markdown className={classes.root} source={data?.termsOfService} />
  ) : null;
}
