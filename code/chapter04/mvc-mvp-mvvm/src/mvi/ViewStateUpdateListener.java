package mvi;

public interface ViewStateUpdateListener {

	void onViewStateUpdate(String targetName, Object value);
}
